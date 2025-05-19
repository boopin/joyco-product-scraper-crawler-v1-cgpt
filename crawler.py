import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os
import logging
import random
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Base URL of the site to crawl
BASE_URL = "https://joyandco.com"

# Storage for visited and product URLs
visited_urls = set()
product_urls = set()
existing_products = set()

# User-Agent rotation for avoiding bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/98.0.4758.85 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Validate if a URL is internal
def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc

# Check for existing products to enable incremental crawling
def load_existing_products():
    global existing_products
    output_csv = "product_urls/product_links.csv"
    
    if os.path.exists(output_csv):
        try:
            with open(output_csv, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                existing_products = set(row["url"] for row in reader)
            logging.info(f"Loaded {len(existing_products)} existing product URLs")
        except Exception as e:
            logging.error(f"Error loading existing products: {e}")

# Recursive crawler to find internal product links
def crawl(url):
    try:
        # Add a random delay between 1-3 seconds to be polite to the server
        time.sleep(random.uniform(1, 3))
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": BASE_URL,
            "DNT": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for HTTP errors
        if response.status_code != 200:
            logging.warning(f"HTTP error {response.status_code} for URL: {url}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for link_tag in soup.find_all("a", href=True):
            href = link_tag['href']
            full_url = urljoin(BASE_URL, href.split("?")[0])
            if is_valid_url(full_url) and full_url.startswith(BASE_URL):
                if full_url not in visited_urls:
                    visited_urls.add(full_url)
                    if "/product/" in full_url:
                        # Only add if not already in our database (for incremental crawling)
                        if full_url not in existing_products:
                            logging.info(f"Found new product: {full_url}")
                            product_urls.add(full_url)
                        else:
                            logging.debug(f"Skipping existing product: {full_url}")
                    else:
                        crawl(full_url)
    except Exception as e:
        logging.error(f"Error crawling {url}: {e}")

# Main fetch function
def fetch_product_links():
    load_existing_products()
    crawl(BASE_URL)
    return product_urls

# Save URLs to CSV
def save_to_csv(urls, filename="product_urls/product_links.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
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
    tree.write(filename, encoding='utf-8', xml_declaration=True)

# Entry point
def main():
    logging.info("Starting crawler")
    
    # Combine existing and new products
    all_product_urls = existing_products.copy()
    new_urls = fetch_product_links()
    all_product_urls.update(new_urls)
    
    save_to_csv(all_product_urls)
    save_to_xml(all_product_urls)
    
    logging.info(f"✅ Saved {len(all_product_urls)} product URLs to product_urls/ (of which {len(new_urls)} are new)")

if __name__ == "__main__":
    main()
