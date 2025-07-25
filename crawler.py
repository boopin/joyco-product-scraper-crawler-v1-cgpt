#!/usr/bin/env python3
import argparse
import os
import sys
import json
import random
import time
import logging
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET

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
STATE_LINKS = "product_urls/product_links.csv"

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
    if parsed.netloc == "" or parsed.netloc == urlparse(BASE_URL).netloc:
        return True
    logger.debug(f"Skipping external URL: {url}")
    return False

def purge_state_files():
    """Delete the old CSV/JSON state files for a full-reset crawl."""
    for fn in (STATE_LINKS, SEEN_PRODUCTS_FILE):
        try:
            os.remove(fn)
            logger.info(f"[force] removed state file: {fn}")
        except FileNotFoundError:
            pass

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
    Save visited and product URLs to JSON for persisting crawler state.
    Includes detailed logging to confirm file creation.
    """
    logger.info("Attempting to save crawler state to seen_products.json...")
    try:
        with open(SEEN_PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "visited_urls": list(visited_urls),
                "product_urls": list(product_urls)
            }, f, indent=2)
        logger.info(f"✅ Successfully saved crawler state to {SEEN_PRODUCTS_FILE}")
        size = os.path.getsize(SEEN_PRODUCTS_FILE)
        logger.info(f"File {SEEN_PRODUCTS_FILE} exists after saving, size: {size} bytes")
    except Exception as e:
        logger.error(f"❌ Failed to save crawler state: {e}")

def process_sitemap():
    """
    Placeholder for sitemap processing if the site had a sitemap.xml.
    Returns False since joyandco.com does not provide one.
    """
    logger.info("Site doesn't have XML sitemap - skipping sitemap processing")
    return False

def crawl_product_listings():
    """
    ENHANCED: Crawl main product listing pages with pagination support.
    Extract product links from listings and collect product URLs with improved discovery.
    """
    logger.info("🔍 ENHANCED: Crawling product listing pages with improved discovery...")

    product_pages = [
        "https://joyandco.com/products",
        "https://joyandco.com/flash-deals",
        "https://joyandco.com/new-arrivals",
        "https://joyandco.com/category/tableware",
        "https://joyandco.com/category/home-decor",
        "https://joyandco.com/category/furniture",
        "https://joyandco.com/category/gift-accessories",
        "https://joyandco.com/category/candles-candle-holders",
        "https://joyandco.com/category/decorative-accents",
        "https://joyandco.com/category/vases-centerpieces",
        "https://joyandco.com/category/wall-art",
        "https://joyandco.com/category/table-linens",
        "https://joyandco.com/category/decorative-cushions",
        "https://joyandco.com/category/home-fragrance",
        "https://joyandco.com/category/side-tables",
        "https://joyandco.com/category/special-occasion-accents"
    ]

    for start_page in product_pages:
        page_url = start_page
        page_num = 1
        has_next_page = True
        page_products = 0

        while has_next_page and page_num <= 50:  # Safety limit
            try:
                logger.info(f"📄 Processing listing page: {page_url} (Page {page_num})")
                headers = {
                    "User-Agent": get_random_user_agent(),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
                
                response = requests.get(page_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # ENHANCED SELECTORS - Multiple ways to find product links
                    product_selectors = [
                        # Original selectors
                        ".products a.btn-shopnow",
                        ".pro-detail a",
                        
                        # Additional comprehensive selectors
                        "a[href*='/product/']",  # Any link containing /product/
                        ".product-item a",
                        ".product-card a", 
                        ".product-link",
                        ".shop-now",
                        "a.product-url",
                        ".product-thumb a",
                        ".item-link",
                        
                        # Grid/list view selectors
                        ".product-grid a",
                        ".product-list a",
                        ".products-grid a",
                        ".products-list a",
                        
                        # E-commerce common patterns
                        ".woocommerce a[href*='product']",
                        ".product a[href]",
                        "[data-product-url]",
                        
                        # JoyAndCo specific patterns
                        ".col-md-4 a",
                        ".col-sm-6 a",
                        ".product-wrapper a",
                        ".item-wrapper a"
                    ]
                    
                    page_found = 0
                    for selector in product_selectors:
                        try:
                            product_links = soup.select(selector)
                            for link in product_links:
                                href = link.get('href') or link.get('data-product-url')
                                if href and "/product/" in href:
                                    full_url = urljoin(BASE_URL, href)
                                    # Clean URL (remove query params)
                                    full_url = full_url.split("?")[0].split("#")[0]
                                    
                                    if full_url not in visited_urls and full_url.startswith(BASE_URL):
                                        logger.info(f"✅ NEW PRODUCT: {full_url}")
                                        visited_urls.add(full_url)
                                        product_urls.add(full_url)
                                        page_found += 1
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e}")
                            continue
                    
                    page_products += page_found
                    logger.info(f"📦 Found {page_found} products on this page (Total: {len(product_urls)})")
                    
                    # Enhanced pagination detection
                    has_next_page = False
                    
                    # Method 1: Look for next page number
                    pagination = soup.select(".page-item a, .pagination a, .pager a")
                    for page_link in pagination:
                        link_text = page_link.get_text().strip()
                        if link_text == str(page_num + 1) or link_text.lower() in ['next', '→', '»']:
                            next_href = page_link.get('href')
                            if next_href:
                                page_url = urljoin(BASE_URL, next_href)
                                page_num += 1
                                has_next_page = True
                                logger.info(f"🔄 Found next page: {page_url}")
                                break
                    
                    # Method 2: Look for "Next" or arrow links
                    if not has_next_page:
                        next_links = soup.select(
                            "a[rel='next'], .next a, .page-next a"
                        )
                        for next_link in next_links:
                            next_href = next_link.get('href')
                            if next_href:
                                page_url = urljoin(BASE_URL, next_href)
                                page_num += 1
                                has_next_page = True
                                logger.info(f"🔄 Found next link: {page_url}")
                                break
                    
                    # Method 3: URL pattern pagination (e.g., ?page=2)
                    if not has_next_page and page_found > 0:
                        if "?" in page_url:
                            base_url = page_url.split("?")[0]
                            next_page_url = f"{base_url}?page={page_num + 1}"
                        else:
                            next_page_url = f"{page_url}{'&' if '?' in page_url else '?'}page={page_num + 1}"
                        
                        # Test if next page exists
                        try:
                            test_response = requests.head(next_page_url, headers=headers, timeout=10)
                            if test_response.status_code == 200:
                                page_url = next_page_url
                                page_num += 1
                                has_next_page = True
                                logger.info(f"🔄 Trying URL pattern pagination: {page_url}")
                        except:
                            pass
                    
                    if not has_next_page:
                        logger.info(f"📄 No more pages found for {start_page}")
                        
                else:
                    logger.warning(f"❌ Failed to access {page_url}: HTTP {response.status_code}")
                    has_next_page = False
                    
            except Exception as e:
                logger.error(f"💥 Error processing {page_url}: {e}")
                has_next_page = False
                
            # Respectful delay between requests
            time.sleep(random.uniform(1.5, 3.0))
        
        logger.info(f"✅ Completed {start_page}: Found {page_products} products across {page_num-1} pages")

    logger.info(f"🎯 TOTAL PRODUCTS DISCOVERED: {len(product_urls)}")

def enhanced_simple_crawl(url, max_depth=3, current_depth=0):
    """
    Enhanced recursive crawler with depth control and better link discovery
    """
    if current_depth >= max_depth:
        logger.debug(f"Max depth {max_depth} reached for {url}")
        return
        
    try:
        if url in visited_urls:
            return
            
        time.sleep(random.uniform(1, 2))
        logger.info(f"🔍 Crawling: {url} (depth: {current_depth})")
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
            logger.warning(f"❌ HTTP {response.status_code} for: {url}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links - enhanced discovery
        all_links = soup.find_all("a", href=True)
        product_links_found = 0
        navigation_links = []
        
        for link_tag in all_links:
            href = link_tag['href']
            
            # Skip javascript and fragment links
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            # Convert to absolute URL
            full_url = urljoin(BASE_URL, href.split("?")[0])
            
            # Must be within our domain
            if not (is_valid_url(full_url) and full_url.startswith(BASE_URL)):
                continue
                
            if full_url in visited_urls:
                continue
                
            # Product URL detection
            if "/product/" in full_url:
                logger.info(f"🆕 DISCOVERED PRODUCT: {full_url}")
                product_urls.add(full_url)
                product_links_found += 1
            else:
                # Collect navigation links for further crawling
                # Prioritize category and listing pages
                if any(keyword in full_url.lower() for keyword in 
                       ['category', 'products', 'collections', 'shop', 'browse', 'new-arrivals', 'flash-deals']):
                    navigation_links.append(full_url)
        
        logger.info(f"📦 Found {product_links_found} products on {url}")
        
        # Recursively crawl navigation links (with depth limit)
        for nav_link in navigation_links[:5]:  # Limit to prevent explosion
            enhanced_simple_crawl(nav_link, max_depth, current_depth + 1)
            
    except Exception as e:
        logger.error(f"💥 Error crawling {url}: {e}")

def save_to_csv(urls, filename=OUTPUT_CSV):
    """Save discovered product URLs to CSV with timestamps."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["url", "timestamp"])
        for url in sorted(urls):
            writer.writerow([url, datetime.utcnow().isoformat()])
    logger.info(f"Saved {len(urls)} URLs to CSV: {filename}")

def save_to_xml(urls, filename=OUTPUT_XML):
    """Save discovered product URLs to XML format."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    root = ET.Element("products")
    for url in sorted(urls):
        product = ET.SubElement(root, "product")
        ET.SubElement(product, "url").text = url
        ET.SubElement(product, "timestamp").text = datetime.utcnow().isoformat()
    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)
    logger.info(f"Saved {len(urls)} URLs to XML: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Crawl site for product URLs, incrementally or full-reset."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Purge previous state files and do a full crawl."
    )
    args = parser.parse_args()

    if args.force:
        purge_state_files()

    logger.info(f"🚀 Starting ENHANCED crawler{' [FORCE]' if args.force else ''}")
    logger.info("=" * 80)
    logger.info("🔧 ENHANCEMENTS:")
    logger.info("   • Multiple comprehensive product selectors")
    logger.info("   • Enhanced pagination detection")
    logger.info("   • More category pages covered")
    logger.info("   • Better error handling and logging")
    logger.info("=" * 80)
    
    load_existing_data()
    process_sitemap()
    
    # Run enhanced product listings crawl
    crawl_product_listings()

    # Enhanced fallback deep crawl if too few products found
    if len(product_urls) < 100:
        logger.info(f"🔄 Only found {len(product_urls)} products. Running enhanced deep crawl...")
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
                enhanced_simple_crawl(start_url, max_depth=2)

    logger.info("=" * 80)
    logger.info(f"✅ CRAWLING COMPLETE")
    logger.info(f"🎯 Found {len(product_urls)} products out of {len(visited_urls)} URLs visited.")
    logger.info("=" * 80)

    if product_urls:
        save_to_csv(product_urls)
        save_to_xml(product_urls)
        save_seen_products()
        logger.info(f"✅ Saved {len(product_urls)} product URLs to {os.path.dirname(OUTPUT_CSV)}/")
        
        # Show some sample URLs for verification
        sample_urls = list(product_urls)[:10]
        logger.info("📝 Sample discovered URLs:")
        for i, url in enumerate(sample_urls, 1):
            logger.info(f"   {i}. {url}")
        
        if len(product_urls) > 10:
            logger.info(f"   ... and {len(product_urls) - 10} more products")
    else:
        logger.error("⚠️ No product URLs found. Please check logs for issues.")
        logger.info("🔍 Troubleshooting suggestions:")
        logger.info("   1. Check if the website structure has changed")
        logger.info("   2. Verify the BASE_URL is accessible")
        logger.info("   3. Review the product selectors in crawl_product_listings()")
        logger.info("   4. Run with --force to clear cache and retry")

if __name__ == "__main__":
    main()
