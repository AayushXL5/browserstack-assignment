"""
validate.py

Self-check script to verify the assignment output is complete.
Run after executing the scraper to confirm everything worked.

Usage:
    python validate.py
"""

import os
import sys
import json

# fix for Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

passed = 0
failed = 0


def check(name, condition, detail=""):
    """Run a single validation check."""
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}")
    if detail:
        print(f"       {detail}")


def validate_output_files():
    """Check that all expected JSON output files exist and are valid."""
    print("\n📁 Output Files")
    print("-" * 40)

    files = {
        "articles_data.json": "Scraped articles",
        "translated_headers.json": "Translated headers",
        "word_analysis.json": "Word frequency analysis",
    }

    for filename, desc in files.items():
        path = os.path.join(OUTPUT_DIR, filename)
        exists = os.path.exists(path)
        check(f"{desc} ({filename})", exists)

        if exists:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                check(f"  Valid JSON", True, f"{len(data)} items")
            except Exception as e:
                check(f"  Valid JSON", False, str(e))


def validate_articles():
    """Verify the scraped articles have the required fields."""
    print("\n📰 Articles Data")
    print("-" * 40)

    path = os.path.join(OUTPUT_DIR, "articles_data.json")
    if not os.path.exists(path):
        check("Articles file exists", False)
        return

    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    check("5 articles scraped", len(articles) == 5, f"Found {len(articles)}")

    for i, art in enumerate(articles, 1):
        has_title = bool(art.get("title"))
        has_content = bool(art.get("content"))
        check(f"Article {i} has title", has_title,
              art.get("title", "")[:60] if has_title else "")
        check(f"Article {i} has content", has_content)


def validate_translations():
    """Verify translations were completed."""
    print("\n🌐 Translations")
    print("-" * 40)

    path = os.path.join(OUTPUT_DIR, "translated_headers.json")
    if not os.path.exists(path):
        check("Translations file exists", False)
        return

    with open(path, "r", encoding="utf-8") as f:
        translations = json.load(f)

    check("5 translations completed", len(translations) == 5,
          f"Found {len(translations)}")

    for i, t in enumerate(translations, 1):
        has_original = bool(t.get("original"))
        has_translated = bool(t.get("translated"))
        different = t.get("original") != t.get("translated")
        check(f"Translation {i} completed", has_original and has_translated and different)


def validate_images():
    """Check if article images were downloaded."""
    print("\n🖼️  Images")
    print("-" * 40)

    if not os.path.exists(IMAGES_DIR):
        check("Images directory exists", False)
        return

    images = [f for f in os.listdir(IMAGES_DIR)
              if f.endswith((".jpg", ".png", ".webp"))]
    check("Images downloaded", len(images) > 0, f"Found {len(images)} images")

    for img in images:
        size = os.path.getsize(os.path.join(IMAGES_DIR, img))
        check(f"  {img}", size > 1000, f"{size:,} bytes")


def validate_code_quality():
    """Quick checks on code structure."""
    print("\n✨ Code Quality")
    print("-" * 40)

    files = ["main.py", "scraper.py", "translator.py",
             "analyzer.py", "browserstack_runner.py"]
    base = os.path.dirname(os.path.abspath(__file__))

    for f in files:
        path = os.path.join(base, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
            has_docstring = '"""' in content[:500]
            check(f"{f} has docstring", has_docstring)
        else:
            check(f"{f} exists", False)


if __name__ == "__main__":
    print("=" * 50)
    print("  BrowserStack Assignment - Validation Report")
    print("=" * 50)

    validate_output_files()
    validate_articles()
    validate_translations()
    validate_images()
    validate_code_quality()

    # summary
    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0
    print("\n" + "=" * 50)
    print(f"  Results: {passed}/{total} checks passed ({pct:.0f}%)")
    print("=" * 50)

    if failed == 0:
        print("\n  🎉 All checks passed! Ready for submission.\n")
    else:
        print(f"\n  ⚠️  {failed} check(s) need attention.\n")
