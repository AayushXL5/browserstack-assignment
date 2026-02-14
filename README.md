# El Pais Opinion Scraper

A Selenium-based web scraper that grabs articles from the El País Opinion section, translates the headers from Spanish to English, and analyzes them for repeated words. Runs cross-browser tests on BrowserStack with 5 parallel sessions.

Built for the **BrowserStack Customer Engineering** technical assignment.

## What it does

1. **Scrapes** the first 5 articles from [El País Opinion](https://elpais.com/opinion/)
2. **Extracts** the title, body text (in Spanish), and cover image for each article  
3. **Translates** article headers from Spanish to English using the Google Translate API (via RapidAPI)
4. **Analyzes** the translated headers to find words that appear more than twice
5. **Saves** results to JSON files in the `output/` folder
6. **Runs** on BrowserStack across 5 parallel browser sessions (3 desktop + 2 mobile)

## Results

### Local Execution
- ✅ 5 articles scraped from El País Opinion section
- ✅ 5 titles translated (Spanish → English)
- ✅ 5 cover images downloaded
- ✅ Word frequency analysis completed
- ✅ All results saved to `output/` folder

### BrowserStack Execution
- ✅ 5 parallel browser sessions
- ✅ Cross-browser scraping verified
- ✅ All sessions marked as passed

| Browser | Platform | Status |
|---------|----------|--------|
| Chrome (latest) | Windows 11 | ✅ Passed |
| Safari (latest) | macOS Ventura | ✅ Passed |
| Firefox (latest) | Windows 10 | ✅ Passed |
| Chrome | Samsung Galaxy S23 | ✅ Passed |
| Safari | iPhone 15 | ✅ Passed |

### Sample Output

**Scraped Articles:**
```
Article 1: "Anexión ilegal de Cisjordania"
Article 2: "Competitividad desde el realismo"
Article 3: "Feminismo de escalera plegable"
Article 4: "Agrupémonos todos"
Article 5: "Termodinámica de un beso"
```

**Translations (ES → EN):**
```
[1] Anexión ilegal de Cisjordania → Illegal annexation of the West Bank
[2] Competitividad desde el realismo → Competitiveness from a realist perspective
[3] Feminismo de escalera plegable → Folding ladder feminism
[4] Agrupémonos todos → Let's all get together
[5] Termodinámica de un beso → Thermodynamics of a kiss
```

## Project Structure

```
├── main.py                 # entry point - CLI with --local and --browserstack flags
├── scraper.py              # Selenium scraper for El Pais Opinion section
├── translator.py           # Spanish to English translation via RapidAPI
├── analyzer.py             # word frequency analysis with stop-word filtering
├── browserstack_runner.py  # parallel BrowserStack execution (5 browsers)
├── validate.py             # self-check script to verify output completeness
├── requirements.txt        # Python dependencies
├── .env.example            # template for API keys
├── output/                 # generated JSON results
│   ├── articles_data.json
│   ├── translated_headers.json
│   └── word_analysis.json
└── images/                 # downloaded article cover images
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

## How to Run

### Run locally (Chrome)

```bash
python main.py --local
```

This opens Chrome, scrapes 5 articles from El País, translates the headers, analyzes word frequency, and saves all results to the `output/` folder.

### Run on BrowserStack (5 parallel browsers)

```bash
python main.py --browserstack
```

Runs the same scraping pipeline on 5 browser/OS combinations in parallel using BrowserStack Automate.

### Validate results

```bash
python validate.py
```

Checks that all output files exist, JSON is valid, articles have required fields, images were downloaded, and code has proper documentation.

## Tech Stack

- **Selenium 4** — browser automation (auto-manages ChromeDriver)
- **RapidAPI Google Translate** — Spanish → English translation
- **BrowserStack Automate** — cloud cross-browser testing
- **Python threading** — parallel execution via `ThreadPoolExecutor`

## Design Decisions

- **Modular architecture**: Each concern (scraping, translation, analysis) lives in its own file for clarity
- **Stop-word filtering**: The analyzer filters out common English words (articles, prepositions, pronouns) for meaningful frequency results
- **Fallback selectors**: The scraper tries multiple CSS selectors for title/content extraction to handle El País's varying page structures
- **Cookie handling**: Automatically dismisses the Didomi cookie consent popup
- **Language verification**: Checks the `lang` attribute to confirm the page is in Spanish before scraping

## Notes

- Some opinion articles are paywalled or text-only (no image). Both cases are handled gracefully
- The word analysis may return empty results if no words appear more than twice — this is correct behavior
- BrowserStack credentials use environment variables for security

## Author

Aayush Gupta — [LinkedIn](https://www.linkedin.com/in/aayush02/) · [GitHub](https://github.com/AayushXL5)
