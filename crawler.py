import cloudscraper
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse
from datetime import datetime

# CONFIG: Test with a single product URL
product_urls = [
    "https://joyandco.com/product/flower-girl-candleholder-yellow-CA8gpn"
]

OUTPUT_JSON = "product_feed.json"
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)

# Load previous feed to compare for is_new logic
def load_previous_feed():
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r") as f:
            return json.load(f)
    return []

def extract_product_data(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.select_one("h1.product-title").text.strip() if soup.select_one("h1.product-title") else ""
    price_el = soup.select_one(".product__price .price-item--regular")
    price = price_el.text.strip().replace("AED", "").strip() if price_el else ""

    desc = soup.select_one("div.product__description") or soup.select_one("div#ProductAccordion-accordion-template--16663949584603__main-0")
    description = desc.get_text(separator=" ").strip() if desc else ""

    image = soup.select_one("img.product__media") or soup.select_one("img.product__media-item")
    image_url = image["src"] if image and image.has_attr("src") else ""

    # Additional fields for Google Shopping
    brand = "Joy & Co"
    mpn = urlparse(url).path.split("/")[-1].split("-")[-1]
    gtin = f"0000000{mpn[-4:]}" if mpn else ""
    availability = "in stock" if "sold out" not in soup.text.lower() else "out of stock"
    category = "Home Decor"  # Hardcoded for now

    return {
        "url": url,
        "title": title,
        "price": price,
        "description": description,
        "image_link": image_url,
        "brand": brand,
        "mpn": mpn,
        "gtin": gtin,
        "availability": availability,
        "product_type": category,
        "is_new": False,  # Default; will be updated later
    }

def update_is_new(current_data, previous_data):
    prev_map = {item["url"]: item for item in previous_data}
    for product in current_data:
        url = product["url"]
        if url not in prev_map:
            product["is_new"] = True
        else:
            old = prev_map[url]
            # Compare major fields for any updates
            fields_to_compare = ["title", "price", "description"]
            product["is_new"] = any(product.get(f) != old.get(f) for f in fields_to_compare)

def save_backup(previous_data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{BACKUP_DIR}/product_feed_{timestamp}.json", "w") as f:
        json.dump(previous_data, f, indent=2)

def save_current_feed(data):
    with open(OUTPUT_JSON, "w") as f:
        json.dump(data, f, indent=2)

def main():
    print("🕵️‍♀️ Starting product crawl...")
    previous_data = load_previous_feed()
    current_data = []

    for url in product_urls:
        try:
            product_data = extract_product_data(url)
            current_data.append(product_data)
        except Exception as e:
            print(f"❌ Error extracting {url}: {e}")

    update_is_new(current_data, previous_data)
    if previous_data:
        save_backup(previous_data)
    save_current_feed(current_data)
    print(f"✅ Crawled {len(current_data)} products and saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
