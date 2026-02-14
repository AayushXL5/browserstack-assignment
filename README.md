# El Pais Opinion Scraper

A Selenium-based web scraper that grabs articles from the El Pais Opinion section, translates the headers from Spanish to English, and analyzes them for repeated words. Also runs cross-browser tests on BrowserStack.

Built for the **BrowserStack Customer Engineering** technical assignment.

## What it does

1. **Scrapes** the first 5 articles from [El Pais Opinion](https://elpais.com/opinion/)
2. **Extracts** the title, body text (in Spanish), and cover image for each article  
3. **Translates** article headers from Spanish to English using the Google Translate API (via RapidAPI)
4. **Analyzes** the translated headers to find words that appear more than twice
5. **Runs** on BrowserStack across 5 parallel browser sessions (3 desktop + 2 mobile)

## Project structure

```
├── main.py                 # entry point - CLI with --local and --browserstack flags
├── scraper.py              # the actual Selenium scraper
├── translator.py           # handles translation via RapidAPI
├── analyzer.py             # word frequency analysis
├── browserstack_runner.py  # parallel BrowserStack execution
├── requirements.txt
├── .env.example            # template for API keys
└── images/                 # downloaded article images go here
```

## Setup

### Prerequisites
- Python 3.8+
- Google Chrome (for local runs)
- BrowserStack account
- RapidAPI key for [Google Translate](https://rapidapi.com/robust-api-robust-api-default/api/google-translate113)

### Install

```bash
pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` to `.env` and fill in your keys:

```
BROWSERSTACK_USERNAME=your_username
BROWSERSTACK_ACCESS_KEY=your_key
RAPIDAPI_KEY=your_rapidapi_key
```

## How to run

### Run locally (Chrome)

```bash
python main.py --local
```

This opens Chrome, goes to El Pais, scrapes 5 articles, translates the headers, and shows the analysis.

### Run on BrowserStack (5 parallel browsers)

```bash
python main.py --browserstack
```

This runs the same thing on 5 browsers simultaneously:

| Browser | Platform |
|---------|----------|
| Chrome (latest) | Windows 11 |
| Safari (latest) | macOS Ventura |
| Firefox (latest) | Windows 10 |
| Chrome | Samsung Galaxy S23 |
| Safari | iPhone 15 |

Results show up on the [BrowserStack Automate Dashboard]([https://automate.browserstack.com/](https://automate.browserstack.com/projects/Default+Project/builds/ElPais+Opinion+Scraper/1?public_token=9a8f4fe2777cff960af2ab5e941248daefece70c18990ba212fa138552c96dec)).

## Tech stack

- **Selenium 4** - browser automation
- **RapidAPI Google Translate** - translation
- **BrowserStack Automate** - cloud cross-browser testing
- **Python threading** - parallel execution

## Things I'd improve with more time

- Better handling of paywalled articles (some return empty content)
- Add retry logic for flaky API calls
- Proper logging instead of print statements
- Support for scraping more than 5 articles
- Unit tests

## Author

Aayush Gupta - [GitHub](https://github.com/AayushXL5)
