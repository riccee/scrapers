# Web Scraper API and Frontend

This project provides a web scraper API using Quart and Playwright, with a React-based frontend to interact with the API.

## Features

Scrapes domain information and competitors from SimilarWeb.
Provides real-time progress updates via WebSockets.
Displays scraped data using a React frontend.
Backend Setup

### Prerequisites
Python 3.8+
Quart
Quart-CORS
Playwright
BeautifulSoup
Socket.IO


## Installation
Clone the repository:
```
git clone https://github.com/riccee/scrapers.git
cd scrapers
```

### Install dependencies:
```
quart quart-cors playwright beautifulsoup4 socketio
playwright install
```
### Run the api:
```
quart run
```

## Frontend Setup
### Prerequisites
Node.js
Yarn
React

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

