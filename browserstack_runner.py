"""
browserstack_runner.py

Handles running the scraper on BrowserStack's cloud infrastructure.
We test across 5 different browser/OS combos in parallel using threads.

Desktop: Chrome (Win11), Firefox (Win10), Safari (macOS Ventura)
Mobile: Samsung Galaxy S23, iPhone 15
"""

import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from dotenv import load_dotenv

from scraper import scrape_articles
from translator import translate_titles
from analyzer import find_repeated_words, print_repeated_words

load_dotenv()

# browserstack credentials from .env
BS_USER = os.getenv("BROWSERSTACK_USERNAME", "")
BS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY", "")
BS_HUB = f"https://{BS_USER}:{BS_KEY}@hub-cloud.browserstack.com/wd/hub"


# the 5 browser configs we want to test on
# mix of 3 desktop + 2 mobile as required
BROWSERS = [
    {
        "name": "Chrome on Windows 11",
        "is_mobile": False,
        "bstack:options": {
            "os": "Windows",
            "osVersion": "11",
            "browserName": "Chrome",
            "browserVersion": "latest",
            "sessionName": "ElPais_Chrome_Win11",
            "buildName": "ElPais Opinion Scraper",
        },
    },
    {
        "name": "Safari on macOS Ventura",
        "is_mobile": False,
        "bstack:options": {
            "os": "OS X",
            "osVersion": "Ventura",
            "browserName": "Safari",
            "browserVersion": "latest",
            "sessionName": "ElPais_Safari_macOS",
            "buildName": "ElPais Opinion Scraper",
        },
    },
    {
        "name": "Firefox on Windows 10",
        "is_mobile": False,
        "bstack:options": {
            "os": "Windows",
            "osVersion": "10",
            "browserName": "Firefox",
            "browserVersion": "latest",
            "sessionName": "ElPais_Firefox_Win10",
            "buildName": "ElPais Opinion Scraper",
        },
    },
    {
        "name": "Samsung Galaxy S23 (Chrome)",
        "is_mobile": True,
        "bstack:options": {
            "deviceName": "Samsung Galaxy S23",
            "osVersion": "13.0",
            "browserName": "Chrome",
            "sessionName": "ElPais_Chrome_GalaxyS23",
            "buildName": "ElPais Opinion Scraper",
        },
    },
    {
        "name": "iPhone 15 (Safari)",
        "is_mobile": True,
        "bstack:options": {
            "deviceName": "iPhone 15",
            "osVersion": "17",
            "browserName": "Safari",
            "sessionName": "ElPais_Safari_iPhone15",
            "buildName": "ElPais Opinion Scraper",
        },
    },
]


def create_driver(browser_config):
    """
    Create a Selenium Remote WebDriver for the given browser config.
    Sets up the right capabilities for BrowserStack.
    """
    opts = browser_config["bstack:options"]
    browser_name = opts.get("browserName", "Chrome")

    # pick the right options class based on browser
    if browser_name == "Safari":
        options = webdriver.SafariOptions()
    elif browser_name == "Firefox":
        options = webdriver.FirefoxOptions()
    else:
        options = webdriver.ChromeOptions()

    # build the bstack capabilities
    bstack_caps = {
        "userName": BS_USER,
        "accessKey": BS_KEY,
        "sessionName": opts.get("sessionName", ""),
        "buildName": opts.get("buildName", ""),
    }

    # desktop vs mobile have different capability fields
    if browser_config["is_mobile"]:
        bstack_caps["deviceName"] = opts["deviceName"]
        bstack_caps["osVersion"] = opts["osVersion"]
    else:
        bstack_caps["os"] = opts.get("os", "")
        bstack_caps["osVersion"] = opts.get("osVersion", "")
        bstack_caps["browserVersion"] = opts.get("browserVersion", "latest")

    options.set_capability("bstack:options", bstack_caps)

    driver = webdriver.Remote(command_executor=BS_HUB, options=options)
    return driver


def run_single_browser(browser_config):
    """
    Run the full scraping + translation + analysis pipeline
    on one BrowserStack browser session.
    """
    name = browser_config["name"]
    print(f"\n{'='*55}")
    print(f"  Starting: {name}")
    print(f"{'='*55}")

    driver = None
    status = "failed"
    reason = ""

    try:
        driver = create_driver(browser_config)

        # run the scraper
        articles = scrape_articles(driver, count=5)

        if articles:
            # translate and analyze
            titles_spanish = [a["title"] for a in articles]
            titles_english = translate_titles(titles_spanish)
            repeated = find_repeated_words(titles_english)
            print_repeated_words(repeated)

            status = "passed"
            reason = f"Scraped {len(articles)} articles successfully"
        else:
            reason = "Could not scrape any articles"

    except Exception as e:
        reason = str(e)
        traceback.print_exc()

    finally:
        if driver:
            # tell browserstack whether the test passed or failed
            try:
                driver.execute_script(
                    'browserstack_executor: {"action": "setSessionStatus", '
                    '"arguments": {"status": "' + status + '", '
                    '"reason": "' + reason.replace('"', '\\"') + '"}}'
                )
            except Exception:
                pass  # don't crash if we can't update status
            driver.quit()

    tag = "[PASS]" if status == "passed" else "[FAIL]"
    print(f"\n{tag} {name} -- {status.upper()}")

    return {"browser": name, "status": status, "reason": reason}


def run_all_browsers():
    """
    Run the scraper on all 5 browsers in parallel.
    Uses ThreadPoolExecutor for concurrent execution.
    """
    print("\n" + "=" * 60)
    print("  BROWSERSTACK PARALLEL EXECUTION")
    print(f"  Running {len(BROWSERS)} browsers with {len(BROWSERS)} threads")
    print("=" * 60)

    results = []

    # each browser gets its own thread
    with ThreadPoolExecutor(max_workers=len(BROWSERS)) as pool:
        future_to_name = {
            pool.submit(run_single_browser, b): b["name"]
            for b in BROWSERS
        }

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "browser": name,
                    "status": "error",
                    "reason": str(e),
                })

    # print a summary at the end
    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    for r in results:
        tag = "[PASS]" if r["status"] == "passed" else "[FAIL]"
        print(f"  {tag} {r['browser']}: {r['reason']}")
    
    passed = sum(1 for r in results if r["status"] == "passed")
    total = len(results)
    print(f"\n  {passed}/{total} browsers passed")
    print("=" * 60)

    return results
