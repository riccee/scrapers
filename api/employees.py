import requests
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
from supabase import create_client, Client
import keys

async def search(domain):
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


