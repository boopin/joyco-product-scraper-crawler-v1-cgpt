import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from datetime import datetime
import os

BASE_URL = "https://joyandco.com"
visited_urls = set()
product_urls = set()

INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "product_urls/product_links.csv"
XML_OUTPUT = "product_urls/product_links.xml"

# Load existing URLs (if any)
def load_existing_urls():
    if not os.path.exists(INPUT_CSV):
        return set()
    with open(INPUT_CSV, newline='') as file:
        reader = csv.DictReader(file)
        return set(row["url"] for row in reader)

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc

def crawl(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link_tag in soup.find_all("a", href=True):
            href = link_tag['href']
            full_url = urljoin(BASE_URL, href.split("?")[0])
            if is_valid_url(full_url) and full_url.startswith(BASE_URL):
                if full_url not in visited_urls:
                    visited_urls.add(full_url)
                    if "/product/" in full_url:
                        product_urls.add(full_url)
                    else:
                        crawl(full_url)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def save_to_csv(urls, previous_urls):
    os.makedirs(os.path.dirname(CSV_OUTPUT), exist_ok=True)
    with open(CSV_OUTPUT, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp", "is_new"])
        for url in sorted(urls):
            is_new = "true" if url not in previous_urls else "false"
            writer.writerow([url, datetime.utcnow().isoformat(), is_new])

def save_to_xml(urls, previous_urls):
    os.makedirs(os.path.dirname(XML_OUTPUT), exist_ok=True)
    root = ET.Element("products")
    for url in sorted(urls):
        product = ET.SubElement(root, "product")
        ET.SubElement(product, "url").text = url
        ET.SubElement(product, "timestamp").text = datetime.utcnow().isoformat()
        ET.SubElement(product, "is_new").text = "true" if url not in previous_urls else "false"
    tree = ET.ElementTree(root)
    tree.write(XML_OUTPUT)

def main():
    previous_urls = load_existing_urls()
    crawl(BASE_URL)
    save_to_csv(product_urls, previous_urls)
    save_to_xml(product_urls, previous_urls)
    print(f"✅ Saved {len(product_urls)} product URLs with 'is_new' flag.")

if __name__ == "__main__":
    main()
