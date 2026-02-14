"""
translator.py

Uses the RapidAPI Google Translate API to translate article titles
from Spanish to English. Free tier, no billing needed.

API docs: https://rapidapi.com/robust-api-robust-api-default/api/google-translate113
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
API_URL = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"

# headers for the RapidAPI request
API_HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": "google-translate113.p.rapidapi.com",
    "x-rapidapi-key": RAPIDAPI_KEY,
}


def translate_titles(titles, src="es", dest="en"):
    """
    Takes a list of Spanish titles and returns their English translations.
    
    Uses the RapidAPI Google Translate endpoint. Each title is translated
    individually (the free tier has a limit so we do them one by one).
    If a translation fails we just keep the original text.
    """
    if not RAPIDAPI_KEY:
        print("[ERROR] RAPIDAPI_KEY not set in .env file!")
        return titles  # return originals if no key

    translated = []

    for i, title in enumerate(titles):
        try:
            body = {
                "from": src,
                "to": dest,
                "text": title
            }

            resp = requests.post(API_URL, json=body, headers=API_HEADERS, timeout=15)
            resp.raise_for_status()
            result = resp.json()

            # the API returns the translated text in the "trans" field
            eng_title = result.get("trans", title)
            translated.append(eng_title)

            print(f"   [{i+1}] {title}")
            print(f"       -> {eng_title}")

        except requests.exceptions.HTTPError as e:
            print(f"   [ERROR] HTTP error for '{title}': {e}")
            translated.append(title)
        except Exception as e:
            # network issue, timeout, etc
            print(f"   [ERROR] Failed to translate '{title}': {e}")
            translated.append(title)

    return translated


# NOTE: if you hit rate limits on the free tier, you might need to add
# a small delay between requests (time.sleep(0.5) or something)
