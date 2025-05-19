# crawler.py

import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# CONFIG - You can later replace this with full dynamic crawl logic
product_urls = [
    "https://joyandco.com/product/flower-girl-candleholder-yellow-CA8gpn"
]

OUTPUT_JSON = "product_data_latest.json"
BACKUP_JSON = f"product_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

def fetch_html(url):
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Failed to fetch {url} - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception fetching {url}: {str(e)}")
        return None

def extract_product_data(url, html):
    soup = BeautifulSoup(html, "html.parser")

    def safe_select(selector):
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else ""

    def safe_attr(selector, attr):
        tag = soup.select_one(selector)
        return tag[attr].strip() if tag and attr in tag.attrs else ""

    return {
        "url": url,
        "title": safe_select("h1"),
        "price": safe_select(".price .price-item"),  # Adjust based on site class
        "image": safe_attr("img.product__media", "src") or safe_attr("img.product__media", "data-src"),
        "brand": "Joy & Co",
        "gtin": safe_select("[itemprop='gtin13'], [itemprop='gtin']"),
        "mpn": safe_select("[itemprop='mpn']"),
        "availability": safe_select("[itemprop='availability']") or "in stock",
        "category": safe_select(".breadcrumb a:last-of-type") or "Home Decor"
    }

def load_previous_data():
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            return {item["url"]: item for item in json.load(f)}
    return {}

def save_data(data):
    # Backup existing data
    if os.path.exists(OUTPUT_JSON):
        os.rename(OUTPUT_JSON, BACKUP_JSON)
        print(f"📦 Created backup: {BACKUP_JSON}")

    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)
        print(f"✅ Saved: {OUTPUT_JSON}")

def main():
    previous_data = load_previous_data()
    all_data = []

    for url in product_urls:
        html = fetch_html(url)
        if not html:
            continue

        product = extract_product_data(url, html)

        # is_new comparison logic
        old = previous_data.get(url)
        product["is_new"] = old != product
        all_data.append(product)

    save_data(all_data)

if __name__ == "__main__":
    main()
