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

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Base URL of the site to crawl
BASE_URL = "https://joyandco.com"
OUTPUT_CSV = "product_urls/product_links.csv"
OUTPUT_XML = "product_urls/product_links.xml"

# Storage for visited and product URLs
visited_urls = set()
product_urls = set()

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
    domain = parsed.netloc
    
    # Ensure we're only following URLs from the same domain
    if domain == "" or domain == urlparse(BASE_URL).netloc:
        return True
    
    logging.debug(f"Skipping external URL: {url}")
    return False

# Check existing URLs and load into memory
def load_existing_data():
    global visited_urls, product_urls
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # Try to load existing products from CSV
    if os.path.exists(OUTPUT_CSV):
        try:
            with open(OUTPUT_CSV, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    url = row.get("url")
                    if url:
                        visited_urls.add(url)
                        if "/product/" in url:
                            product_urls.add(url)
                            
            logging.info(f"Loaded {len(product_urls)} existing product URLs")
        except Exception as e:
            logging.error(f"Error loading existing products: {e}")
    else:
        logging.info("No existing product file found. Starting fresh crawl.")

# Placeholder function for sitemap processing - site doesn't have XML sitemap
def process_sitemap():
    logging.info("Site doesn't have XML sitemap - skipping sitemap processing")
    return False

# Crawl product listings with pagination
def crawl_product_listings():
    logging.info("Crawling product listings pages")
    
    # Main product listing URLs - expanded to include more starting points
    product_pages = [
        "https://joyandco.com/products",
        "https://joyandco.com/flash-deals",
        "https://joyandco.com/new-arrivals",
        "https://joyandco.com/category/tableware", 
        "https://joyandco.com/category/home-decor",
        "https://joyandco.com/category/furniture",
        "https://joyandco.com/category/gift-accessories"
    ]
    
    # Crawl each starting page and handle pagination
    for start_page in product_pages:
        page_url = start_page
        page_num = 1
        has_next_page = True
        
        while has_next_page:
            try:
                logging.info(f"Processing listing page: {page_url} (Page {page_num})")
                headers = {
                    "User-Agent": get_random_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                }
                
                response = requests.get(page_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for product cards with links
                    product_links = soup.select(".products a.btn-shopnow, .pro-detail a")
                    if product_links:
                        for product_link in product_links:
                            href = product_link.get('href')
                            if href and "/product/" in href:
                                full_url = urljoin(BASE_URL, href)
                                if full_url not in visited_urls:
                                    logging.info(f"Found product URL: {full_url}")
                                    visited_urls.add(full_url)
                                    product_urls.add(full_url)
                    
                    # Check for pagination and find next page link
                    has_next_page = False
                    pagination = soup.select(".page-item a")
                    for page_link in pagination:
                        if page_link.get_text().strip() == str(page_num + 1):
                            next_page_url = urljoin(BASE_URL, page_link.get('href'))
                            page_url = next_page_url
                            page_num += 1
                            has_next_page = True
                            break
                            
                    # Also look for "Next" link
                    next_links = soup.select(".page-item a[rel='next']")
                    if next_links and not has_next_page:
                        next_page_url = urljoin(BASE_URL, next_links[0].get('href'))
                        page_url = next_page_url
                        page_num += 1
                        has_next_page = True
                else:
                    logging.warning(f"Failed to access listing page: {page_url}, status: {response.status_code}")
                    has_next_page = False
                    
            except Exception as e:
                logging.error(f"Error processing listing page {page_url}: {e}")
                has_next_page = False
            
            # Be polite and wait
            time.sleep(random.uniform(1, 2))

# Simple crawler without depth restrictions - similar to the original working crawler
def simple_crawl(url):
    try:
        # Don't crawl if we've already visited this URL
        if url in visited_urls:
            return
            
        # Add a random delay between 1-2 seconds to be polite to the server
        time.sleep(random.uniform(1, 2))
        
        # Log the URL we're crawling
        logging.info(f"Crawling URL: {url}")
        visited_urls.add(url)
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": BASE_URL,
            "DNT": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check for HTTP errors
        if response.status_code != 200:
            logging.warning(f"HTTP error {response.status_code} for URL: {url}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links
        all_links = soup.find_all("a", href=True)
        for link_tag in all_links:
            href = link_tag['href']
            # Skip anchor links and javascript
            if href.startswith('#') or href.startswith('javascript:'):
                continue
                
            full_url = urljoin(BASE_URL, href.split("?")[0])
            if is_valid_url(full_url) and full_url.startswith(BASE_URL) and full_url not in visited_urls:
                
                # Process product URLs
                if "/product/" in full_url:
                    logging.info(f"Found product URL: {full_url}")
                    product_urls.add(full_url)
                
                # Continue crawling non-product pages
                simple_crawl(full_url)
                    
    except Exception as e:
        logging.error(f"Error crawling {url}: {e}")

# Save URLs to CSV
def save_to_csv(urls, filename=OUTPUT_CSV):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp"])
        for url in sorted(urls):
            writer.writerow([url, datetime.utcnow().isoformat()])
    logging.info(f"Saved {len(urls)} URLs to CSV: {filename}")

# Save URLs to XML
def save_to_xml(urls, filename=OUTPUT_XML):
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
    logging.info(f"Saved {len(urls)} URLs to XML: {filename}")

# Entry point
def main():
    logging.info("Starting crawler")
    
    # Load existing data first
    load_existing_data()
    
    # Try to process sitemap first (fastest method if available)
    sitemap_found = process_sitemap()
    
    # Crawl product listings with pagination
    crawl_product_listings()
    
    # If we still don't have enough products, use simple crawler
    if len(product_urls) < 100:
        logging.info(f"Only found {len(product_urls)} products. Using simple crawler for more thorough search.")
        starting_urls = [
            BASE_URL,
            "https://joyandco.com/products",
            "https://joyandco.com/flash-deals",
            "https://joyandco.com/new-arrivals",
            "https://joyandco.com/category/tableware",
            "https://joyandco.com/category/home-decor",
            "https://joyandco.com/category/furniture",
            "https://joyandco.com/category/gift-accessories"
        ]
        
        # Use the simpler approach that worked in the original crawler
        for start_url in starting_urls:
            if start_url not in visited_urls:
                simple_crawl(start_url)
    
    # Log the counts
    logging.info(f"Found {len(product_urls)} product URLs out of {len(visited_urls)} total URLs visited")
    
    # If we found any products, save them
    if product_urls:
        save_to_csv(product_urls)
        save_to_xml(product_urls)
        print(f"✅ Saved {len(product_urls)} product URLs to product_urls/")
    else:
        logging.error("NO PRODUCT URLS FOUND! Something is wrong with the crawler.")
        print("⚠️ No product URLs found. Check logs for more information.")

if __name__ == "__main__":
    main()
