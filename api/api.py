from  quart import Quart, request, jsonify
from quart_cors import cors
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from employees import search
import requests
import json
import socketio


app = Quart(__name__)
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins='*')
app.asgi_app = socketio.ASGIApp(sio, app.asgi_app)
app = cors(app, allow_origin="*")


@app.route('/api/domain_info', methods=['POST', 'PUT', 'GET'])
async def get_domain_info():
    competitors = {}
    overview = {}
    url = await request.get_json()
    url = url.get('domain')
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        #Actor.config.headless
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        try:
            # Open the URL in a new Playwright page
            page = await context.new_page()
            await page.goto("https://www.similarweb.com/website/"+url+"/competitors/")
            button_exists = await page.query_selector('.app-more-less-text__button') is not None
            if button_exists:
                await page.click('.app-more-less-text__button')


            # Push the title of the page into the default dataset
            soup = BeautifulSoup(await page.content())
            #Overview
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
            try:
                await sio.emit('progress', 20)
            except:
                pass
            #Competitors
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

            overview = {'domain': domain, 'description' : description, 'globalRank' : globalRank, 'globalRankChange' : globalRankChange, 'country':country, 'countryRank':countryRank, "totalVisits" :totalVisit}


            totalEmployees = []
            for idx, domain in enumerate(domains):
                try:
                    employees = await search(domain)
                    print(employees)
                    totalEmployees.append(employees)
                except:
                    totalEmployees.append([])
                try:
                    await sio.emit('progress', 20 + (idx + 1) * 5)
                except:
                    pass
            competitors = [{"domain": domain, "totalVisits" : totalVisit, "categoryId" : categoryId, "categoryRank" : categoryRank, "description": description, "similarity" : similarity, "employees" : employee} for domain, description, totalVisit, categoryId, categoryRank, similarity, employee in zip(domains, descriptions, totalVisits, categoryIds, categoryRanks, similarities, totalEmployees)]

            employee = await search(url)
            overview["employees"] = employee
            try:
                await sio.emit('progress', 100)
            except:
                pass
            response_data= {'overview': overview, 'competitors': competitors}
            return json.dumps(response_data, indent=4)
            #return OrderedDict([('overview', overview), ('competitors', competitors)])
        except Exception:
            return(f'Cannot extract data from {url}.')
        finally:
            await page.close()

