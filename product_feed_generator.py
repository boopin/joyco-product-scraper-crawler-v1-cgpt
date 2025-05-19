import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os

# Input and output paths
INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "google_feed/google_product_feed.csv"  # ✅ Updated filename
XML_OUTPUT = "google_feed/product_feed.xml"

# Ensure output directory exists
os.makedirs("google_feed", exist_ok=True)

def extract_product_data(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title fallback: h1 → <title>
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else (soup.title.string.strip() if soup.title else "No Title")

        # Description fallback: meta[name=description] → first <p>
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            description = desc_tag['content'].strip()
        else:
            p_tag = soup.find("p")
            description = p_tag.get_text(strip=True) if p_tag else "No Description"

        # Image fallback: meta property og:image
        image_tag = soup.find("meta", property="og:image")
        image_link = image_tag['content'] if image_tag else ""

        # Price fallback: meta[itemprop=price] → span.price (adjust selector if needed)
        price_tag = soup.find("meta", attrs={"itemprop": "price"})
        if price_tag:
            price = price_tag['content']
        else:
            price_span = soup.find("span", class_="price")
            if price_span:
                price = price_span.get_text(strip=True).replace("AED", "").replace(",", "").strip()
            else:
                price = "0.00"

        return {
            "id": url.split("/")[-1],
            "title": title,
            "description": description,
            "link": url,
            "image_link": image_link,
            "availability": "in stock",
            "price": f"{price} AED",
            "brand": "Joy & Co",
            "condition": "new"
        }

    except Exception as e:
        print(f"❌ Failed to extract {url}: {e}")
        return None

def generate_csv(products):
    with open(CSV_OUTPUT, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=products[0].keys())
        writer.writeheader()
        for product in products:
            writer.writerow(product)

def generate_xml(products):
    root = ET.Element("products")
    for p in products:
        product = ET.SubElement(root, "product")
        for k, v in p.items():
            el = ET.SubElement(product, k)
            el.text = v
    tree = ET.ElementTree(root)
    tree.write(XML_OUTPUT)

def main():
    urls = []
    with open(INPUT_CSV, newline='') as file:
        reader = csv.DictReader(file)
        urls = [row["url"] for row in reader]

    products = []
    for url in urls:
        data = extract_product_data(url)
        if data:
            products.append(data)

    if products:
        generate_csv(products)
        generate_xml(products)
        print(f"✅ Generated feed for {len(products)} products.")
    else:
        print("⚠️ No products were processed.")

if __name__ == "__main__":
    main()
