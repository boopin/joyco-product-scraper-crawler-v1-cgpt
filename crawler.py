import cloudscraper
from bs4 import BeautifulSoup
import json
import os

def fetch_product_details(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(response.text, "lxml")

    def extract_text(selector):
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""

    def extract_attr(selector, attr):
        element = soup.select_one(selector)
        return element.get(attr) if element else ""

    return {
        "url": url,
        "title": extract_text("h1"),
        "price": extract_text(".price-item--regular") or extract_text(".price"),
        "description": extract_text(".product__description") or extract_text(".rte"),
        "image_link": extract_attr("img.product__media", "src") or extract_attr("img", "src"),
        "brand": "Joy & Co",  # Set statically or extract dynamically
        "availability": "in stock",  # Default value, can be improved
        "category": "Home Decor",  # Static for now
        "gtin": "",  # GTIN not present in Joy & Co, leave blank
        "mpn": "",   # MPN not present, leave blank
    }

def load_previous():
    if os.path.exists("product_feed.json"):
        with open("product_feed.json", "r") as f:
            return json.load(f)
    return []

def save_products(products):
    with open("product_feed.json", "w") as f:
        json.dump(products, f, indent=2)

def is_new_product(url, previous_data):
    return not any(p["url"] == url for p in previous_data)

def main():
    product_urls = [
        "https://joyandco.com/product/flower-girl-candleholder-yellow-CA8gpn"
    ]
    previous_data = load_previous()
    all_products = []

    for url in product_urls:
        data = fetch_product_details(url)
        if data:
            data["is_new"] = is_new_product(url, previous_data)
            all_products.append(data)

    save_products(all_products)
    print(f"✅ Saved {len(all_products)} product(s) to product_feed.json")

if __name__ == "__main__":
    main()
