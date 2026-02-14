"""
main.py

Entry point for the BrowserStack technical assignment.
Scrapes El Pais Opinion articles, translates headers, analyzes word frequency.

Usage:
    python main.py --local          run with local Chrome
    python main.py --browserstack   run on BrowserStack (5 browsers, parallel)
"""

import argparse
import os
import sys
import time

# fix for windows console not handling unicode well
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from selenium import webdriver
from dotenv import load_dotenv

from scraper import scrape_articles
from translator import translate_titles
from analyzer import find_repeated_words, print_repeated_words

load_dotenv()


def show_banner():
    print("\n" + "=" * 60)
    print("  El Pais - Opinion Section Scraper")
    print("  BrowserStack Technical Assignment")
    print("=" * 60)


def display_articles(articles):
    """Print all scraped articles with their Spanish titles and content."""
    print("\n" + "=" * 60)
    print("  SCRAPED ARTICLES (Spanish)")
    print("=" * 60)

    for i, art in enumerate(articles, 1):
        print(f"\n{'-' * 50}")
        print(f"  Article {i}")
        print(f"{'-' * 50}")
        print(f"  Title: {art['title']}")
        print(f"  URL:   {art['url']}")
        if art['image_path']:
            print(f"  Image: {art['image_path']}")
        
        print(f"\n  Content:")
        for line in art['content'].split('\n'):
            if line.strip():
                print(f"    {line.strip()}")
        print()


def display_translations(spanish, english):
    """Show the original and translated headers side by side."""
    print("\n" + "=" * 60)
    print("  TRANSLATED HEADERS (ES -> EN)")
    print("=" * 60)
    for i, (es, en) in enumerate(zip(spanish, english), 1):
        print(f"\n  [{i}] {es}")
        print(f"      -> {en}")


def run_local():
    """Run everything locally using Chrome."""
    print("\nRunning locally with Chrome...\n")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=es")
    # this hides the "Chrome is being controlled by automated software" bar
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # selenium 4 handles chromedriver automatically, no need for webdriver-manager
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        t0 = time.time()

        # step 1: scrape the articles
        print("\n" + "=" * 60)
        print("  STEP 1: Scraping articles from El Pais Opinion section")
        print("=" * 60)
        articles = scrape_articles(driver, count=5)

        if not articles:
            print("[ERROR] No articles found! Something went wrong.")
            return

        display_articles(articles)

        # step 2: translate the headers
        print("\n" + "=" * 60)
        print("  STEP 2: Translating headers to English")
        print("=" * 60)
        spanish_titles = [a["title"] for a in articles]
        english_titles = translate_titles(spanish_titles)
        display_translations(spanish_titles, english_titles)

        # step 3: analyze for repeated words
        print("\n" + "=" * 60)
        print("  STEP 3: Analyzing translated headers")
        print("=" * 60)
        repeated = find_repeated_words(english_titles)
        print_repeated_words(repeated)

        elapsed = time.time() - t0
        print(f"\nDone! Took {elapsed:.1f} seconds")

    finally:
        driver.quit()


def run_browserstack():
    """Run on BrowserStack with 5 parallel browser sessions."""
    print("\nRunning on BrowserStack (5 parallel browsers)...\n")

    from browserstack_runner import run_all_browsers
    results = run_all_browsers()

    passed = sum(1 for r in results if r["status"] == "passed")
    if passed == len(results):
        print("\nAll browsers passed!")
    else:
        print(f"\n{passed}/{len(results)} browsers passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="El Pais Opinion Scraper - BrowserStack Assignment"
    )
    parser.add_argument("--local", action="store_true",
                        help="Run locally with Chrome")
    parser.add_argument("--browserstack", action="store_true",
                        help="Run on BrowserStack (5 parallel browsers)")

    args = parser.parse_args()

    show_banner()

    if not args.local and not args.browserstack:
        print("\nPlease specify a mode:")
        print("  python main.py --local")
        print("  python main.py --browserstack")
        sys.exit(1)

    if args.local:
        run_local()

    if args.browserstack:
        run_browserstack()
