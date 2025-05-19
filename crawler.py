import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os

# Base URL of the site to crawl
BASE_URL = "https://joyandco.com"

# Storage for visited and product URLs
visited_urls = set()
product_urls = set()

# Validate if a URL is internal
def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc

# Recursive crawler to find internal product links
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

# Main fetch function
def fetch_product_links():
    crawl(BASE_URL)
    return product_urls

# Save URLs to CSV
def save_to_csv(urls, filename="product_urls/product_links.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp"])
        for url in sorted(urls):
            writer.writerow([url, datetime.utcnow().isoformat()])

# Save URLs to XML
def save_to_xml(urls, filename="product_urls/product_links.xml"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    root = ET.Element("products")
    for url in sorted(urls):
        product = ET.SubElement(root, "product")
        url_el = ET.SubElement(product, "url")
        url_el.text = url
        timestamp_el = ET.SubElement(product, "timestamp")
        timestamp_el.text = datetime.utcnow().isoformat()
    tree = ET.ElementTree(root)
    tree.write(filename)

# Entry point
def main():
    urls = fetch_product_links()
    save_to_csv(urls)
    save_to_xml(urls)
    print(f"✅ Saved {len(urls)} product URLs to product_urls/")

if __name__ == "__main__":
    main()
