
import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os
import logging
import re
import random
import json
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Read URLs from crawler output
INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "google_feed/product_feed.csv"
XML_OUTPUT = "google_feed/product_feed.xml"
GOOGLE_MERCHANT_CSV = "google_feed/google_merchant_feed.csv"

# Ensure output directories exist
os.makedirs("google_feed", exist_ok=True)
logging.info(f"Ensured google_feed directory exists")

# Google Product Category Mapping (basic - add more based on your products)
CATEGORY_MAPPING = {
    "Tableware": "6208",  # Home & Garden > Kitchen & Dining > Tableware
    "Candles": "3655",    # Home & Garden > Decor > Candles & Home Fragrances
    "Cushions": "635",    # Home & Garden > Decor > Throw Pillows
    "Vases": "644",       # Home & Garden > Decor > Vases
    "Wall Art": "639",    # Home & Garden > Decor > Artwork
    "Side Tables": "6357" # Home & Garden > Furniture > Tables > Side Tables
}

# Default fallback Google category for home decor
DEFAULT_GOOGLE_CATEGORY = "635" # Home & Garden > Decor

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

def map_to_google_category(category_name):
    """Map Joy&Co category to Google's product taxonomy"""
    # Look for keywords in the category
    for keyword, google_id in CATEGORY_MAPPING.items():
        if keyword.lower() in category_name.lower():
            return google_id
    return DEFAULT_GOOGLE_CATEGORY

def extract_product_data(url):
    try:
        logging.info(f"Extracting data from: {url}")
        
        # Add a random delay between 1-2 seconds to be polite to the server
        time.sleep(random.uniform(1, 2))
        
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://joyandco.com/",
            "DNT": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check for HTTP errors
        if response.status_code == 404:
            logging.error(f"Product not found (404): {url}")
            return None
        elif response.status_code == 403:
            logging.error(f"Access forbidden (403): {url}")
            return None
        elif response.status_code != 200:
            logging.error(f"HTTP error {response.status_code}: {url}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product ID from URL
        product_id = url.split("/")[-1]
        
        # Get title from the product detail h2
        title_tag = soup.select_one(".col-md-6 h2")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        logging.info(f"Title extracted: {title}")
        
        # Get full description from class="text-body" div in #description
        description_div = soup.select_one("#description .text-body")
        description = description_div.get_text(strip=True) if description_div else "No Description"
        logging.info(f"Description extracted: {len(description)} characters")
        
        # Get editor notes and brand info for richer description
        editor_notes_div = soup.select_one("#editor_notes .text-body")
        brand_info_div = soup.select_one("#about_the_brand .text-body")
        
        editor_notes = editor_notes_div.get_text(strip=True) if editor_notes_div else ""
        brand_info = brand_info_div.get_text(strip=True) if brand_info_div else ""
        
        # Create rich structured description
        rich_description = description
        if editor_notes:
            rich_description += f"\n\nEDITOR'S NOTE:\n{editor_notes}"
        if brand_info:
            rich_description += f"\n\nABOUT THE BRAND:\n{brand_info}"
        
        # Get all product images
        image_elements = soup.select(".cz-preview-item img")
        all_images = []
        for img in image_elements:
            if 'src' in img.attrs:
                if img['src'] not in all_images:  # Avoid duplicates
                    all_images.append(img['src'])
        
        # Get primary image from meta tag
        image_tag = soup.find("meta", property="og:image")
        image_link = image_tag['content'] if image_tag else ""
        if not image_link and all_images:
            image_link = all_images[0]  # Use first image as fallback
            
        # Remove primary image from additional_images to avoid duplication
        additional_images = [img for img in all_images if img != image_link]
        
        # Get price from the .price div
        price_div = soup.select_one(".price")
        price = "0.00"
        if price_div:
            price_text = price_div.get_text(strip=True)
            # Extract numeric price
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_text)
            if price_match:
                price = price_match.group(1)
                
                # Ensure price has 2 decimal places for Google Merchant format
                if '.' not in price:
                    price = f"{price}.00"
                elif len(price.split('.')[1]) == 1:
                    price = f"{price}0"
                    
        logging.info(f"Price extracted: {price}")
        
        # Get brand from the p.pic-info
        brand_tag = soup.select_one("p.pic-info")
        brand = brand_tag.get_text(strip=True) if brand_tag else "Joy & Co"
        logging.info(f"Brand extracted: {brand}")
        
        # Extract category breadcrumbs
        breadcrumbs = []
        breadcrumb_elements = soup.select(".breadcrumbs a")
        for crumb in breadcrumb_elements[1:-1]:  # Skip home and product
            breadcrumbs.append(crumb.get_text(strip=True))
        
        category = " > ".join(breadcrumbs) if breadcrumbs else "Uncategorized"
        
        # Map to Google product category
        google_product_category = map_to_google_category(category)
        
        # Check if product is in stock
        stock_status = "in stock"
        out_of_stock_element = soup.select_one(".out-of-stock-label")
        if out_of_stock_element:
            stock_status = "out of stock"
            
        # Extract variants if available (for future use)
        variants = []
        variant_elements = soup.select(".quantity-cart select option")
        if variant_elements:
            for variant_el in variant_elements[1:]:  # Skip the first option if it's a placeholder
                variant_name = variant_el.get_text(strip=True)
                variant_value = variant_el.get('value', '')
                if variant_name and variant_value:
                    variants.append({"name": variant_name, "value": variant_value})

        # Look for product code as MPN (Manufacturer Part Number)
        mpn = ""
        code_info = soup.select_one(".code-info")
        if code_info:
            code_match = re.search(r'Product code - (\w+)', code_info.get_text(strip=True))
            if code_match:
                mpn = code_match.group(1)
        
        # If no MPN found, use the product ID
        if not mpn:
            mpn = product_id

        product_data = {
            "id": product_id,
            "title": title,
            "description": description,
            "rich_description": rich_description,
            "link": url,
            "image_link": image_link,
            "additional_image_link": additional_images[0] if additional_images else "",
            "additional_images": additional_images,
            "availability": stock_status,
            "price": f"{price} AED",
            "brand": brand,
            "condition": "new",
            "category": category,
            "google_product_category": google_product_category,
            "mpn": mpn,
            "gtin": "",  # Not available from the website
            "variants": json.dumps(variants) if variants else ""
        }
        
        # Log the extracted data
        logging.info(f"Successfully extracted data for product: {product_data['id']}")
        
        return product_data
    except Exception as e:
        logging.error(f"Failed to extract data from {url}: {e}")
        return None

def generate_csv(products):
    try:
        logging.info(f"Generating CSV at {CSV_OUTPUT} with {len(products)} products")
        
        # Define core fields for CSV export (excluding rich fields and arrays)
        csv_fields = ["id", "title", "description", "link", "image_link", 
                      "availability", "price", "brand", "condition", "category"]
        
        # Convert all values to strings for CSV compatibility
        string_products = []
        for product in products:
            string_product = {}
            for field in csv_fields:
                value = product.get(field, "")
                string_product[field] = str(value) if value is not None else ""
            string_products.append(string_product)
        
        with open(CSV_OUTPUT, mode='w', newline='', encoding='utf-8') as file:
            if not products:
                logging.warning("No products to write to CSV")
                return False
                
            writer = csv.DictWriter(file, fieldnames=csv_fields)
            writer.writeheader()
            for product in string_products:
                writer.writerow(product)
        
        # Verify file was created
        if os.path.exists(CSV_OUTPUT):
            file_size = os.path.getsize(CSV_OUTPUT)
            logging.info(f"CSV file successfully created at {CSV_OUTPUT}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"CSV file was not created at {CSV_OUTPUT}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating CSV file: {e}")
        return False

def generate_google_merchant_feed(products):
    try:
        logging.info(f"Generating Google Merchant feed at {GOOGLE_MERCHANT_CSV} with {len(products)} products")
        
        # Define required Google Merchant fields
        google_fields = [
            "id", "title", "description", "link", "image_link", "additional_image_link",
            "availability", "price", "brand", "condition", "google_product_category", 
            "mpn", "gtin"
        ]
        
        # Convert all values to strings for CSV compatibility
        google_products = []
        for product in products:
            google_product = {}
            for field in google_fields:
                value = product.get(field, "")
                google_product[field] = str(value) if value is not None else ""
            google_products.append(google_product)
        
        with open(GOOGLE_MERCHANT_CSV, mode='w', newline='', encoding='utf-8') as file:
            if not products:
                logging.warning("No products to write to Google Merchant feed")
                return False
                
            writer = csv.DictWriter(file, fieldnames=google_fields)
            writer.writeheader()
            for product in google_products:
                writer.writerow(product)
        
        # Verify file was created
        if os.path.exists(GOOGLE_MERCHANT_CSV):
            file_size = os.path.getsize(GOOGLE_MERCHANT_CSV)
            logging.info(f"Google Merchant feed successfully created at {GOOGLE_MERCHANT_CSV}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"Google Merchant feed was not created at {GOOGLE_MERCHANT_CSV}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating Google Merchant feed: {e}")
        return False

def generate_xml(products):
    try:
        logging.info(f"Generating XML at {XML_OUTPUT} with {len(products)} products")
        
        root = ET.Element("products")
        for p in products:
            product = ET.SubElement(root, "product")
            
            # Add simple string elements
            for k, v in p.items():
                # Skip complex elements that need special handling
                if k in ["additional_images", "variants"]:
                    continue
                    
                el = ET.SubElement(product, k)
                # Explicitly convert value to string if not None
                el.text = str(v) if v is not None else ""
            
            # Handle additional images as child elements
            if p.get("additional_images"):
                images_el = ET.SubElement(product, "additional_images")
                for img_url in p["additional_images"]:
                    img_el = ET.SubElement(images_el, "image")
                    img_el.text = img_url
            
            # Handle variants if present
            if p.get("variants") and p["variants"]:
                try:
                    variants_data = json.loads(p["variants"])
                    if variants_data:
                        variants_el = ET.SubElement(product, "variants")
                        for variant in variants_data:
                            variant_el = ET.SubElement(variants_el, "variant")
                            for k, v in variant.items():
                                var_attr = ET.SubElement(variant_el, k)
                                var_attr.text = str(v)
                except Exception as e:
                    logging.error(f"Error processing variants for product {p.get('id')}: {e}")
        
        tree = ET.ElementTree(root)
        tree.write(XML_OUTPUT, encoding='utf-8', xml_declaration=True)
        
        # Verify file was created
        if os.path.exists(XML_OUTPUT):
            file_size = os.path.getsize(XML_OUTPUT)
            logging.info(f"XML file successfully created at {XML_OUTPUT}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"XML file was not created at {XML_OUTPUT}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating XML file: {e}")
        return False

def main():
    logging.info("Starting product feed generator")
    
    try:
        # Verify input file exists
        if not os.path.exists(INPUT_CSV):
            logging.error(f"Input file does not exist: {INPUT_CSV}")
            return
            
        urls = []
        with open(INPUT_CSV, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            urls = [row["url"] for row in reader]
        
        logging.info(f"Read {len(urls)} URLs from {INPUT_CSV}")

        products = []
        for url in urls:
            data = extract_product_data(url)
            if data:
                products.append(data)

        logging.info(f"Processed {len(products)} products out of {len(urls)} URLs")

        if products:
            # Create a test product to debug CSV generation
            test_product = products[0]
            logging.info(f"Debug - First product: {test_product['title']}")
            
            # Create the standard feeds
            xml_success = generate_xml(products)
            csv_success = generate_csv(products)
            
            # Create the Google Merchant feed
            google_success = generate_google_merchant_feed(products)
            
            if csv_success and xml_success and google_success:
                print(f"✅ Successfully generated feeds for {len(products)} products.")
            else:
                if not csv_success:
                    print(f"⚠️ Failed to generate standard CSV feed.")
                if not xml_success:
                    print(f"⚠️ Failed to generate XML feed.")
                if not google_success:
                    print(f"⚠️ Failed to generate Google Merchant feed.")
        else:
            logging.warning("No products were processed.")
            print("⚠️ No products were processed.")
            
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import time
    main()
