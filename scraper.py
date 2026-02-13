"""
scraper.py

Selenium-based scraper for El Pais Opinion section.
Grabs the first 5 articles, extracts their title/content,
and downloads any cover images it finds.
"""

import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# where we'll save downloaded images
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")


def ensure_image_dir():
    """Make sure the images folder exists."""
    os.makedirs(IMAGE_DIR, exist_ok=True)


def accept_cookies(driver):
    """
    El Pais shows a cookie consent popup (Didomi) on first visit.
    This tries to click the accept button so it doesn't block our scraping.
    If it doesn't show up within 5s, we just move on.
    """
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        btn.click()
        time.sleep(1)
    except Exception:
        pass  # no cookie popup, that's fine


def check_language(driver):
    """
    Check that the page is in Spanish by looking at the html lang attribute.
    The assignment says we need to verify it's in Spanish.
    """
    html = driver.find_element(By.TAG_NAME, "html")
    lang = html.get_attribute("lang") or ""
    if lang.startswith("es"):
        print("[OK] Page is in Spanish (lang='es')")
        return True
    else:
        # sometimes it might show a different lang, just warn and continue
        print(f"[WARN] Expected lang='es' but got '{lang}'. Continuing anyway...")
        return False


def get_article_links(driver, num_articles=5):
    """
    Go to the Opinion section and grab the first N article URLs.
    
    The page has <article> elements with <h2> links inside them.
    We collect those href values.
    """
    url = "https://elpais.com/opinion/"
    print(f"\nNavigating to: {url}")
    driver.get(url)
    time.sleep(3)  # let the page load fully

    accept_cookies(driver)
    check_language(driver)

    links = []

    # primary method: look for article > h2 > a
    try:
        articles = driver.find_elements(By.CSS_SELECTOR, "article")
        for art in articles:
            try:
                a_tag = art.find_element(By.CSS_SELECTOR, "h2 a")
                href = a_tag.get_attribute("href")
                if href and href not in links:
                    links.append(href)
                    if len(links) >= num_articles:
                        break
            except Exception:
                continue
    except Exception:
        pass

    # fallback if we didn't get enough links
    if len(links) < num_articles:
        try:
            all_h2_links = driver.find_elements(By.CSS_SELECTOR, "h2 a[href*='/opinion/']")
            for a in all_h2_links:
                href = a.get_attribute("href")
                if href and href not in links:
                    links.append(href)
                    if len(links) >= num_articles:
                        break
        except Exception:
            pass

    print(f"Found {len(links)} article links")
    return links[:num_articles]


def scrape_single_article(driver, url, idx):
    """
    Visit an article page and extract:
    - title (from h1)
    - body content (from article paragraphs)
    - cover image (if there is one)
    """
    driver.get(url)
    time.sleep(2)

    data = {
        "url": url,
        "title": "",
        "content": "",
        "image_path": None
    }

    # get the title
    # el pais uses different structures sometimes so we try a few selectors
    try:
        h1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article header h1"))
        )
        data["title"] = h1.text.strip()
    except Exception:
        try:
            h1 = driver.find_element(By.CSS_SELECTOR, "h1.a_t")
            data["title"] = h1.text.strip()
        except Exception:
            try:
                h1 = driver.find_element(By.TAG_NAME, "h1")
                data["title"] = h1.text.strip()
            except Exception:
                data["title"] = "(could not extract title)"

    # get the article body
    try:
        # try the main content area first
        paragraphs = driver.find_elements(
            By.CSS_SELECTOR,
            "article .a_c p, article .article_body p, "
            "article [data-dtm-region='articulo_cuerpo'] p"
        )
        if not paragraphs:
            # fallback to any <p> inside <article>
            paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")
        
        text_parts = [p.text.strip() for p in paragraphs if p.text.strip()]
        data["content"] = "\n".join(text_parts)
    except Exception:
        data["content"] = "(could not extract content)"

    # try to get the cover image
    try:
        img = driver.find_element(By.CSS_SELECTOR, "article figure img, article .a_m_w img")
        img_url = img.get_attribute("src")
        if img_url:
            data["image_path"] = download_image(img_url, idx)
    except Exception:
        # many opinion articles are text-only, no image
        data["image_path"] = None

    return data


def download_image(img_url, idx):
    """Download an image and save it to the images folder."""
    ensure_image_dir()
    try:
        resp = requests.get(img_url, timeout=15, stream=True)
        resp.raise_for_status()

        # figure out file extension from content type
        ctype = resp.headers.get("Content-Type", "")
        if "png" in ctype:
            ext = "png"
        elif "webp" in ctype:
            ext = "webp"
        else:
            ext = "jpg"  # default

        filename = f"article_{idx + 1}_cover.{ext}"
        filepath = os.path.join(IMAGE_DIR, filename)

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)

        print(f"   [IMG] Saved: {filename}")
        return filepath

    except Exception as e:
        print(f"   [WARN] Could not download image: {e}")
        return None


def scrape_articles(driver, count=5):
    """
    Main function - scrapes `count` articles from the Opinion section.
    Returns a list of dicts with title, content, url, image_path.
    """
    article_urls = get_article_links(driver, count)
    results = []

    for i, url in enumerate(article_urls):
        print(f"\n--- Article {i + 1}/{len(article_urls)} ---")
        print(f"   URL: {url}")

        article = scrape_single_article(driver, url, i)
        results.append(article)

        print(f"   Title: {article['title']}")
        # just show a preview of the content so the output isn't too long
        preview = article['content'][:150]
        if len(article['content']) > 150:
            preview += "..."
        print(f"   Content: {preview}")

        if article['image_path']:
            print(f"   Image: {article['image_path']}")
        else:
            print(f"   (no cover image)")

    return results


# TODO: add support for scraping more than 5 articles (pagination)
# TODO: handle paywalled articles better - right now we just get empty content
