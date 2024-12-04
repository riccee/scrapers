from  quart import Quart, request, jsonify, Response, websocket
from quart_cors import cors
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import json
from supabase import create_client, Client
import keys
from openai import OpenAI


app = Quart(__name__)

connections = {}  
client = OpenAI(api_key = keys.aikey)

@app.websocket('/api/ws')
async def ws():
    # Get connetion ID from client and add connection to connections dict
    connection_id = await websocket.receive()
    await websocket.send(connection_id)
    if connection_id:
        connections[connection_id] = [websocket._get_current_object(), 10]

    # Keep connection alive and handle connection health
    try:
        while True:
            await connections[connection_id][0].receive()
    except asyncio.CancelledError:
        raise
    except Exception as e:
        app.logger.info(f"WebSocket connection closed with error: {e}")
    finally:    
        if connection_id in connections:
            del connections[connection_id]

# Fetch function for asycronous https requests
async def fetch(session, url, payload, headers):
    async with session.post(url, json=payload, headers=headers) as response:
        return await response.json()

async def search_employees(domain):
    # Check if domain is in the db
    url = keys.url
    key= keys.supakey
    supabase: Client = create_client(url, key) 
    response = supabase.table('Employees').select("*").eq('domain', domain).execute()
    if response.data:
        return json.loads(response.data[0]["employees"])

    # Get the slug from domain name for scraping theOrg
    url = "https://prod-graphql-api.theorg.com/graphql"
    payload = {
        "query": "query search($query: String!) { searchCompanies(query: $query) { id slug name type status extension verificationType verified logoImage { ...ImageFragment __typename } __typename } } fragment ImageFragment on Image { endpoint ext uri versions __typename }",
        "variables": {"query": domain}
    }    
    headers = {
    'accept': '*/*',
    'content-type' : 'application/json',
    'origin': 'https://theorg.com',
    'referer': 'https://theorg.com/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  }

    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, payload, headers)
        try:
            slug = response['data']['searchCompanies'][0]['slug']
        except (KeyError, IndexError):
            return []
    
    # Scrape theOrg
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        cookies = keys.cookies
        #implements cookies so we can go to website
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        try:
            await page.goto("https://theorg.com/org/"+slug+"/")

            soup = BeautifulSoup(await page.content(), features="html.parser")
            
            users = [user.get_text(strip=True) for user in soup.find_all('span', {'class':'PositionCard_name__iERDX'})]

            positions = [position.get_text(strip=True) for position in soup.find_all('div', {'class':'PositionCard_role__XNUly'})]
        
            total = dict(zip(users, positions))
            employees = {key: value for key, value in total.items()}

            # Push to database
            if employees:
                data, count = supabase.table('Employees').insert({"domain": domain, "employees": employees}).execute() 
            
            await browser.close()
            return employees
        except Exception as e:
            return({'test' : f'Cannot extract data from {url}. The error is {e}'})

@app.route('/api/domain_info', methods=['POST'])
async def get_domain():
    # Get the URL and connection_id from the post request
    try:
        url = await request.get_json()
        connection_id = url.get('connection_id')
        url = url.get('domain')
    except:
        return jsonify([])
    
    # Make sure connection_id is in the dict
    while True:
        if connection_id in connections:
            break
        await asyncio.sleep(0.1)
    
    #Push progress to client
    await connections[connection_id][0].send(json.dumps({'progress': connections[connection_id][1]}))

    async with async_playwright() as playwright:
        #setup playwright

        await connections[connection_id][0].send(json.dumps({'progress': connections[connection_id][1]+20}))

        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        page = await context.new_page()
        try:
            # Open the URL in a new Playwright page
            await page.goto("https://www.similarweb.com/website/"+url+"/competitors/")
            if await page.query_selector('.app-more-less-text__button'):
                await page.click('.app-more-less-text__button')

            # Setup bs4
            soup = BeautifulSoup(await page.content(), features="html.parser")
            await connections[connection_id][0].send(json.dumps({'progress': connections[connection_id][1]+40}))

            # Get the url overview
            domain_info = {
                'domain': soup.find('p', {'class': 'wa-overview__title'}).get_text(strip=True) if soup.find('p', {'class': 'wa-overview__title'}) else '',
                'description': soup.find('div', {"class": "app-more-less-text"}).get_text(strip=True).replace("Show less", "").strip() if soup.find('div', {"class": "app-more-less-text"}) else '',
                'globalRank': soup.find('p', {"class": "wa-rank-list__value"}).get_text(strip=True) if soup.find('p', {"class": "wa-rank-list__value"}) else '',
                'globalRankChange': soup.find('span', {"class": "app-parameter-change app-parameter-change--md app-parameter-change--up"}).get_text(strip=True) if soup.find('span', {"class": "app-parameter-change app-parameter-change--md app-parameter-change--up"}) else '',
                'country': soup.find('div', {"class": "wa-rank-list__info"}).get_text(strip=True) if soup.find('div', {"class": "wa-rank-list__info"}) else '',
                'countryRank': soup.find_all('p', {"class": "wa-rank-list__value"})[1].get_text(strip=True) if len(soup.find_all('p', {"class": "wa-rank-list__value"})) > 1 else '',
                'totalVisits': soup.find('p', {"class": "engagement-list__item-value"}).get_text(strip=True) if soup.find('p', {"class": "engagement-list__item-value"}) else '',
                'employees': await search_employees(url)            
                }
            await connections[connection_id][0].send(json.dumps({'progress': connections[connection_id][1]+60}))
            
            # Get the competitors overview
            competitors = []
            domains = [d.get_text(strip=True) for d in soup.find_all('a', {"class": 'wa-competitors-card__website-title'})]
            descriptions = [d.get_text(strip=True) for d in soup.find_all('p', {"class": 'wa-competitors-card__website-description'}, {'data-test': "total-visits"})]
            totalVisits = [v.get_text(strip=True) for v in soup.find_all('p', {"class": 'engagement-list__item-value'})][4:][::4]
            categoryIds = [c.get_text(strip=True) for c in soup.find_all('div', {"class": 'wa-rank-list__info'})][2:][1::2] if len(totalVisits) == 9 else [c.get_text(strip=True) for c in soup.find_all('div', {"class": 'wa-rank-list__info'})][1::2]
            categoryRanks = [r.get_text(strip=True) for r in soup.find_all('p', {"class": "wa-rank-list__value"})][5:][::3]
            similarities = [s.get_text(strip=True) for s in soup.find_all('span', {"class": "app-progress wa-competitors-card__affinity-progress"})]
            

            await connections[connection_id][0].send(json.dumps({'progress': connections[connection_id][1]+80}))

            # Search employees for every competitor
            #tasks = [search_employees(domain) for domain in domains]
            #totalEmployees = await asyncio.gather(*tasks)
            totalEmployees = []
            for domain in domains:
                totalEmployees.append(await search_employees(domain))

            # Format Json
            for domain, description, totalVisit, categoryId, categoryRank, similarity, employee in zip(domains, descriptions, totalVisits, categoryIds, categoryRanks, similarities, totalEmployees):
                competitors.append({
                    "domain": domain,
                    "totalVisits": totalVisit,
                    "categoryId": categoryId,
                    "categoryRank": categoryRank,
                    "description": description,
                    "similarity": similarity,
                    "employees": employee
                })

            response_data= {'overview': domain_info, 'competitors': competitors}
            await connections[connection_id][0].send(json.dumps({'progress': 100}))

            try:
                chat_completion = client.chat.completions.create(
                messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following company information: {response_data}",
                }
                ],
                model="gpt-3.5-turbo",
                )
                summary = chat_completion.choices[0].message.content
                response_data['summary'] = summary
            except Exception as e:
                return f"Error generating summary: {e}"
            
            return json.dumps(response_data, indent=4)

        except Exception as e:
            return(f'Cannot extract data from {url}. The error is {e}')
        finally:
            await page.close()
