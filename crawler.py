import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse
from google.colab import files

# Base URL
BASE_URL = "https://joyandco.com"

# Set to hold unique internal URLs
visited_urls = set()
product_urls = set()

def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc

def crawl(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link_tag in soup.find_all("a", href=True):
            href = link_tag['href']
            full_url = urljoin(BASE_URL, href.split("?")[0])

            if is_valid_url(full_url) and full_url.startswith(BASE_URL):
                if full_url not in visited_urls:
                    visited_urls.add(full_url)

                    # If it's a product URL
                    if "/product/" in full_url:
                        product_urls.add(full_url)
                    # Continue crawling if it's an internal page
                    elif BASE_URL in full_url:
                        crawl(full_url)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Start crawl
crawl(BASE_URL)

# Save product URLs to CSV
filename = "product_urls.csv"
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Product URL"])
    for url in sorted(product_urls):
        writer.writerow([url])

# Auto-download CSV
files.download(filename)

# Summary
print(f"Found {len(product_urls)} product URLs")

Crawler Script to crawl & scrape Joy&Co all Product URLs

// crawler.py

import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Example: list of product page URLs to crawl
product_urls = [
    "https://example.com/product1",
    "https://example.com/product2",
    # add your product URLs here or crawl dynamically
]

def fetch_product_links():
    # This is a placeholder for crawling logic.
    # For now, it returns the static list.
    return product_urls

def save_to_csv(urls, filename="product_links.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp"])
        for url in urls:
            writer.writerow([url, datetime.utcnow().isoformat()])

def save_to_xml(urls, filename="product_links.xml"):
    root = ET.Element("products")
    for url in urls:
        product = ET.SubElement(root, "product")
        url_el = ET.SubElement(product, "url")
        url_el.text = url
        timestamp_el = ET.SubElement(product, "timestamp")
        timestamp_el.text = datetime.utcnow().isoformat()
    tree = ET.ElementTree(root)
    tree.write(filename)

def main():
    urls = fetch_product_links()
    save_to_csv(urls)
    save_to_xml(urls)
    print(f"Saved {len(urls)} product URLs to CSV and XML.")

if __name__ == "__main__":
    main()
