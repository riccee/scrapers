# Web Scraper API and Frontend

My first website and webscraping project! This project provides a web scraper API using Quart and Playwright, with a React-based frontend to interact with the Quart API. The official website is hosted at http://www.riccee.com/.
## Features

Scrapes domain information and competitors from SimilarWeb and employee information from theorg.
Provides real-time progress updates via WebSockets.
Displays scraped data using a React frontend.

## Installation
Clone the repository:
```
git clone https://github.com/riccee/scrapers.git
cd scrapers
```

## Backend Setup

### Prerequisites
- Python 3.8+ 
- Quart 
- Quart-cors 
- Playwright 
- BeautifulSoup 


### Install dependencies:
```
pip3 install quart quart-cors playwright beautifulsoup4
playwright install
```
### Run the api:
```
quart run
```

## Frontend Setup

### Prerequisites
- Node.js
- Yarn
- React

### Installation
```
yarn install
```

### Start the development server:
```
react-scripts start
```

## Usage
Open your browser and navigate to http://localhost:3000.
Enter a domain name and submit.
View the progress and results.

## Acknowledgements
Thanks to the Quart, Playwright, and React teams for their awesome libraries. I've had an amazing time making this project.

