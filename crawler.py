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
import sys
import json
import subprocess

# Configure detailed logging to stdout with timestamp and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Base site URL to restrict crawling within the domain
BASE_URL = "https://joyandco.com"

# Output files for collected product URLs
OUTPUT_CSV = "product_urls/product_links.csv"
OUTPUT_XML = "product_urls/product_links.xml"

# JSON file to persist visited and product URLs
SEEN_PRODUCTS_FILE = "seen_products.json"

# Global sets to track visited URLs and identified product URLs
visited_urls = set()
product_urls = set()

# User-Agent list for rotation to avoid bot detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (iPad; CPU OS 15_2 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) CriOS/98.0.4758.85 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    """Return a random User-Agent string from the list."""
    return random.choice(USER_AGENTS)

def is_valid_url(url):
    """
    Check if a URL belongs to the same domain as BASE_URL.
    Avoids crawling external links.
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain == "" or domain == urlparse(BASE_URL).netloc:
        return True
    logger.debug(f"Skipping external URL: {url}")
    return False

def load_existing_data():
    """
    Load previously visited URLs and product URLs from CSV and seen_products.json, if exists,
    to avoid duplicates in the current crawl.
    """
    global visited_urls, product_urls
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Load from CSV
    if os.path.exists(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    url = row.get("url")
                    if url:
                        visited_urls.add(url)
                        if "/product/" in url:
                            product_urls.add(url)
                        count += 1
            logger.info(f"Loaded {len(product_urls)} existing product URLs from CSV ({count} total URLs)")
        except Exception as e:
            logger.error(f"Error loading existing products CSV: {e}")
    else:
        logger.info("No existing product URLs file found. Starting fresh crawl.")

    # Load from JSON cache file for speed and more accurate state
    if os.path.exists(SEEN_PRODUCTS_FILE):
        try:
            with open(SEEN_PRODUCTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                visited_urls.update(set(data.get("visited_urls", [])))
                product_urls.update(set(data.get("product_urls", [])))
            logger.info(f"Cache HIT: Loaded {len(product_urls)} product URLs and {len(visited_urls)} visited URLs from {SEEN_PRODUCTS_FILE}")
        except Exception as e:
            logger.error(f"Error loading {SEEN_PRODUCTS_FILE}: {e}")
    else:
        logger.info(f"Cache MISS: No {SEEN_PRODUCTS_FILE} found, will create new.")

def save_seen_products():
    """
    Save visited and product URLs to JSON for persisting crawler state,
    then log file details to confirm existence and size.
    """
    try:
        with open(SEEN_PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "visited_urls": list(visited_urls),
                "product_urls": list(product_urls)
            }, f, indent=2)
        logger.info(f"Cache SAVED: Crawler state saved to {SEEN_PRODUCTS_FILE}")

        # Log file details after saving
        ls_output = subprocess.run(['ls', '-la', SEEN_PRODUCTS_FILE], capture_output=True, text=True)
        logger.info(f"File listing for {SEEN_PRODUCTS_FILE}:\n{ls_output.stdout}")
        size = os.path.getsize(SEEN_PRODUCTS_FILE)
        logger.info(f"File size: {size} bytes")

    except Exception as e:
        logger.error(f"Failed to save crawler state to {SEEN_PRODUCTS_FILE}: {e}")

def process_sitemap():
    """
    Placeholder for sitemap processing if the site had a sitemap.xml.
    Returns False since joyandco.com does not provide one.
    """
    logger.info("Site doesn't have XML sitemap - skipping sitemap processing")
    return False

def crawl_product_listings():
    """
    Crawl main product listing pages with pagination support.
    Extract product links from listings and collect product URLs.
    """
    logger.info("Crawling product listing pages with pagination...")

    product_pages = [
        "https://joyandco.com/products",
        "https://joyandco.com/flash-deals",
        "https://joyandco.com/new-arrivals",
        "https://joyandco.com/category/tableware",
        "https://joyandco.com/category/home-decor",
        "https://joyandco.com/category/furniture",
        "https://joyandco.com/category/gift-accessories"
    ]

    for start_page in product_pages:
        page_url = start_page
        page_num = 1
        has_next_page = True

        while has_next_page:
            try:
                logger.info(f"Processing listing page: {page_url} (Page {page_num})")
                headers = {
                    "User-Agent": get_random_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                response = requests.get(page_url, headers=headers, timeout=15)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find product links from specific selectors
                    product_links = soup.select(".products a.btn-shopnow, .pro-detail a")
                    if product_links:
                        for link in product_links:
                            href = link.get('href')
                            if href and "/product/" in href:
                                full_url = urljoin(BASE_URL, href)
                                if full_url not in visited_urls:
                                    logger.info(f"Found product URL: {full_url}")
                                    visited_urls.add(full_url)
                                    product_urls.add(full_url)

                    # Pagination: Check if there is a next page by looking at page numbers or 'next' link
                    has_next_page = False
                    pagination = soup.select(".page-item a")
                    for page_link in pagination:
                        if page_link.get_text().strip() == str(page_num + 1):
                            next_page_url = urljoin(BASE_URL, page_link.get('href'))
                            page_url = next_page_url
                            page_num += 1
                            has_next_page = True
                            break

                    if not has_next_page:
                        next_links = soup.select(".page-item a[rel='next']")
                        if next_links:
                            next_page_url = urljoin(BASE_URL, next_links[0].get('href'))
                            page_url = next_page_url
                            page_num += 1
                            has_next_page = True

                else:
                    logger.warning(f"Failed to access listing page: {page_url} with status {response.status_code}")
                    has_next_page = False

            except Exception as e:
                logger.error(f"Error processing listing page {page_url}: {e}")
                has_next_page = False

            # Politeness delay to avoid hammering server
            time.sleep(random.uniform(1, 2))

def simple_crawl(url):
    """
    Recursive simple crawler for discovering product URLs.
    Crawls all internal links, adds product URLs to the set.
    """
    try:
        if url in visited_urls:
            return

        time.sleep(random.uniform(1, 2))  # Polite crawl delay

        logger.info(f"Crawling URL: {url}")
        visited_urls.add(url)

        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": BASE_URL,
            "DNT": "1"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            logger.warning(f"HTTP {response.status_code} error for URL: {url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags with href
        all_links = soup.find_all("a", href=True)
        for link_tag in all_links:
            href = link_tag['href']

            # Skip anchors and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue

            full_url = urljoin(BASE_URL, href.split("?")[0])
            if (is_valid_url(full_url) and full_url.startswith(BASE_URL)
                    and full_url not in visited_urls):
                if "/product/" in full_url:
                    logger.info(f"Found product URL: {full_url}")
                    product_urls.add(full_url)

                # Continue crawling non-product pages recursively
                simple_crawl(full_url)

    except Exception as e:
        logger.error(f"Error crawling {url}: {e}")

def save_to_csv(urls, filename=OUTPUT_CSV):
    """
    Save discovered product URLs to CSV with timestamps.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp"])
        for url in sorted(urls):
            writer.writerow([url, datetime.utcnow().isoformat()])
    logger.info(f"Saved {len(urls)} URLs to CSV: {filename}")

def save_to_xml(urls, filename=OUTPUT_XML):
    """
    Save discovered product URLs to XML format.
    """
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
    logger.info(f"Saved {len(urls)} URLs to XML: {filename}")

def main():
    logger.info("Starting crawler")

    load_existing_data()

    sitemap_found = process_sitemap()

    crawl_product_listings()

    # Fallback: if fewer than 100 products, run deep crawl
    if len(product_urls) < 100:
        logger.info(f"Only found {len(product_urls)} products. Running simple recursive crawl.")
        starting_points = [
            BASE_URL,
            "https://joyandco.com/products",
            "https://joyandco.com/flash-deals",
            "https://joyandco.com/new-arrivals",
            "https://joyandco.com/category/tableware",
            "https://joyandco.com/category/home-decor",
            "https://joyandco.com/category/furniture",
            "https://joyandco.com/category/gift-accessories"
        ]
        for start_url in starting_points:
            if start_url not in visited_urls:
                simple_crawl(start_url)

    logger.info(f"Finished crawling. Found {len(product_urls)} products out of {len(visited_urls)} URLs visited.")

    if product_urls:
        save_to_csv(product_urls)
        save_to_xml(product_urls)
        save_seen_products()
        logger.info(f"✅ Saved {len(product_urls)} product URLs to {os.path.dirname(OUTPUT_CSV)}/")
    else:
        logger.error("⚠️ No product URLs found. Please check logs for issues.")

if __name__ == "__main__":
    main()
