import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os

# Input/output paths
INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "google_feed/google_product_feed.csv"
XML_OUTPUT = "google_feed/product_feed.xml"

# Ensure output folder exists
os.makedirs("google_feed", exist_ok=True)

def extract_product_data(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Title ---
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else (soup.title.string.strip() if soup.title else "No Title")

        # --- Description ---
        description = "No Description"
        try:
            # Locate 'DESCRIPTION' heading and fetch next sibling div
            desc_heading = soup.find(lambda tag: tag.name in ["h2", "div"] and "DESCRIPTION" in tag.get_text(strip=True).upper())
            if desc_heading:
                desc_container = desc_heading.find_next_sibling("div")
                if desc_container:
                    description = desc_container.get_text(strip=True)
        except Exception:
            pass

        # --- Image ---
        image_tag = soup.find("meta", property="og:image")
        image_link = image_tag['content'] if image_tag else ""

        # --- Price ---
        price = "0.00"
        try:
            price_span = soup.find("span", class_="product__price")
            if price_span:
                price = price_span.get_text(strip=True).replace("AED", "").replace(",", "").strip()
        except Exception:
            pass

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
