from  quart import Quart, request, jsonify, websocket
from quart_cors import cors
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
#from employees import search
import requests
import json
from supabase import create_client, Client
import keys


app = Quart(__name__)
app = cors(app, allow_origin="*")

async def search_employees(domain):
    #check if domain is in the db
    url = keys.url
    key= keys.key
    supabase: Client = create_client(url, key) 
    response = supabase.table('Employees').select("*").execute()
    for i in response.data:
        if domain == i["domain"]:
            return json.loads(i["employees"])

    #if not in db, scrape the data from theorg
        
    # get the slug from domain name
    url = "https://prod-graphql-api.theorg.com/graphql"
    payload = "{\"query\":\"query search($query: String!) {\\n  searchCompanies(query: $query) {\\n    id\\n    slug\\n    name\\n    type\\n    status\\n    extension\\n    verificationType\\n    verified\\n    logoImage {\\n      ...ImageFragment\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment ImageFragment on Image {\\n  endpoint\\n  ext\\n  uri\\n  versions\\n  __typename\\n}\",\"variables\":{\"query\":\""+ domain + "\"}}"
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://theorg.com',
    'priority': 'u=1, i',
    'referer': 'https://theorg.com/',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  }

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        slug = response.json()['data']['searchCompanies'][0]['slug']
    except:
        return(['test'])
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        cookies = keys.cookies
        #implements cookies so we can go to website
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        await page.goto("https://theorg.com/org/"+slug+"/")

        totalUsers = []
        totalPositions = []

        soup = BeautifulSoup(await page.content(), "html.parser")
        
        users = soup.find_all('span', {'class':'PositionCard_name__iERDX'})
        users = [user.get_text(strip=True) for user in users]
        
        positions = soup.find_all('div', {'class':'PositionCard_role__XNUly'})
        positions = [position.get_text(strip=True) for position in positions]

        totalUsers.append(users) 
        totalPositions.append(positions)
    
        #removes all duplicates from the list
        totalUsers = [item for sublist in totalUsers for item in sublist]
        totalPositions = [item for sublist in totalPositions for item in sublist]
        total = dict(zip(totalUsers, totalPositions))
        employees = {}
        for key, value in total.items():
            if key not in employees:
                employees[key] = value

        #push to database
        if employees != {}:
            data, count = supabase.table('Employees').insert({"domain": domain, "employees": employees}).execute() 
        
        return employees


@app.route('/api/domain_info', methods=['POST'])
async def get_domain():
    #get the URL from the post request
    try:
        competitors = {}
        overview = {}
        url = await request.get_json()
        url = url.get('domain')
    except:
        return []

    async with async_playwright() as playwright:
        #setup playwright
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        try:
            # Open the URL in a new Playwright page
            page = await context.new_page()
            await page.goto("https://www.similarweb.com/website/"+url+"/competitors/")
            button_exists = await page.query_selector('.app-more-less-text__button') is not None
            if button_exists:
                await page.click('.app-more-less-text__button')

            #setup bs4
            soup = BeautifulSoup(await page.content())
            
            #get the url overview
            domain = soup.find('p', {'class': 'wa-overview__title'})
            domain = domain.get_text(strip=True) if domain else ""

            description = soup.find('div', {"class": "app-more-less-text"})
            description = description.get_text(strip=True).replace("Show less", "").strip() if description else ""

            globalRank = soup.find('p', {"class": "wa-rank-list__value"})
            globalRank = globalRank.get_text(strip=True) if globalRank else ""

            globalRankChange = soup.find('span', {"class": "app-parameter-change app-parameter-change--md app-parameter-change--up"})
            globalRankChange = globalRankChange.get_text(strip=True) if globalRankChange else ""

            country = soup.find('div', {"class": "wa-rank-list__info"})
            country = country.get_text(strip=True) if country else ""

            countryRanks = soup.find_all('p', {"class": "wa-rank-list__value"})
            countryRank = countryRanks[1].get_text(strip=True) if countryRanks and len(countryRanks) > 1 else ""

            totalVisit = soup.find('p', {"class": "engagement-list__item-value"})
            totalVisit = totalVisit.get_text(strip=True) if totalVisit else ""

            #get the competitors overview
            domains = soup.find_all('a', {"class" : 'wa-competitors-card__website-title'})
            domains = [domain.get_text(strip=True) for domain in domains]

            descriptions = soup.find_all('p', {"class" : 'wa-competitors-card__website-description'}, {'data-test' : "total-visits"})
            descriptions = [description.get_text(strip=True) for description in descriptions]

            totalVisits = soup.find_all('p', {"class" : 'engagement-list__item-value'})
            totalVisits = [totalVisit.get_text(strip=True) for totalVisit in totalVisits][4:][::4]

            categoryIds = soup.find_all('div', {"class": 'wa-rank-list__info'})
            categoryIds = [categoryId.get_text(strip=True) for categoryId in categoryIds][2:][1::2] if len(totalVisits) == 9 else [categoryId.get_text(strip=True) for categoryId in categoryIds][1::2]

            categoryRanks = soup.find_all('p', {"class" : "wa-rank-list__value"})
            categoryRanks = [categoryRank.get_text(strip=True) for categoryRank in categoryRanks][5:][::3]

            similarities = soup.find_all('span', {"class" : "app-progress wa-competitors-card__affinity-progress"})
            similarities = [similarity.get_text(strip=True) for similarity in similarities]

            #get employees for input URL 
            employee = await search_employees(url)

            #construct dictionary for the main URL
            overview = {'domain': domain, 'description' : description, 'globalRank' : globalRank, 'globalRankChange' : globalRankChange, 'country':country, 'countryRank':countryRank, "totalVisits" :totalVisit, "employees": employee}

            #get employees for each of the competitors
            totalEmployees = []
            for idx, domain in enumerate(domains):
                try:
                    employees = await search_employees(domain)
                    totalEmployees.append(employees)
                except:
                    totalEmployees.append([])

            #construct dictionary for the competitors
            competitors = [{"domain": domain, "totalVisits" : totalVisit, "categoryId" : categoryId, "categoryRank" : categoryRank, "description": description, "similarity" : similarity, "employees" : employee} for domain, description, totalVisit, categoryId, categoryRank, similarity, employee in zip(domains, descriptions, totalVisits, categoryIds, categoryRanks, similarities, totalEmployees)]

            response_data= {'overview': overview, 'competitors': competitors}
            return json.dumps(response_data, indent=4)

        except Exception as e:
            return(f'Cannot extract data from {url}.')
        finally:
            await page.close()

