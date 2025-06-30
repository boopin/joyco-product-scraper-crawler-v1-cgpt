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
import time

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

# ═══════════════════════════════════════════════════════════════════════════════════════
# UPDATED Google Product Category Mapping - Based on Manual Google Sheet Assignments
# Updated on June 26, 2025 to match your preferred categorization from 242 products
# ═══════════════════════════════════════════════════════════════════════════════════════

CATEGORY_MAPPING = {
    # ═══════════════════════════════════════════════════════════════
    # TABLEWARE & DINING (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Coffee Cups & Mugs → Category 6049 (Home & Garden > Kitchen & Dining > Tableware > Drinkware > Coffee & Tea Cups)
    "Tableware": "3553",                # Changed from 6208 to 3553 (Plates category)
    "Cups": "6049",                     # Changed from 6231 to 6049 (Coffee & Tea Cups)
    "Mugs": "6049",                     # Changed from 6231 to 6049 (Coffee & Tea Cups)  
    "Coffee": "6049",                   # Changed from 6231 to 6049 (Coffee & Tea Cups)
    "Tea": "6049",                      # Changed from 6231 to 6049 (Coffee & Tea Cups)
    "Coffee Cups": "6049",              # Coffee & Tea Cups
    "Tea Cups": "6049",                 # Coffee & Tea Cups
    "Cappuccino": "6049",               # Coffee & Tea Cups
    "Mug": "6049",                      # Coffee & Tea Cups
    
    # Plates → Category 3553 (Home & Garden > Kitchen & Dining > Tableware > Plates)
    "Plates": "3553",                   # Changed from 6210 to 3553
    "Dinner Plate": "3553",             # Plates
    "Dessert Plate": "3553",            # Plates
    "Deep Plate": "3553",               # Plates
    "Serving Plate": "3553",            # Plates
    "Round Serving Plate": "3553",      # Plates
    "Plate": "3553",                    # Plates
    "Dinnerware": "3553",               # Changed from 6208 to 3553
    "Dinner Set": "3553",               # Changed from 6208 to 3553
    
    # Bowls → Category 3498 (Home & Garden > Kitchen & Dining > Tableware > Bowls)
    "Bowls": "3498",                    # Changed from 6209 to 3498
    "Bowl": "3498",                     # Bowls
    
    # Glasses & Drinkware → Category 674 or 2951
    "Glasses": "674",                   # Changed from 6228 to 674 (Glassware & Drinkware)
    "Glass": "674",                     # Glassware & Drinkware
    "Cocktail Glass": "674",            # Glassware & Drinkware
    "Tumblers": "2951",                 # Based on your Hobnail Tumblers assignment
    "Tumbler": "2951",                  # Tumblers
    
    # Serving Items → Category 674
    "Serving Plates": "3553",           # Changed from 734 to 3553 (consistent with plates)
    "Cake Stand": "674",                # Based on Crystal Cake Stand assignment
    "Serving": "3553",                  # Plates category
    
    # Jugs & Teapots → Category 3330 (Home & Garden > Kitchen & Dining > Tableware > Serveware > Pitchers & Carafes)
    "Jug": "3330",                      # Based on Hobnail Jug assignment
    "Teapot": "3330",                   # Teapots
    "Pitcher": "3330",                  # Pitchers & Carafes
    "Hobnail": "3330",                  # Based on your Hobnail product assignments
    
    # Other Cutlery
    "Cutlery": "728",                   # Keep existing
    
    # ═══════════════════════════════════════════════════════════════
    # HOME DECOR (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Vases → Category 602 (Home & Garden > Decor > Vases) - YOUR MOST COMMON CATEGORY
    "Vases": "602",                     # Changed from 644 to 602
    "Vase": "602",                      # Vases
    "Tower Vase": "602",                # Vases
    
    # Candle Holders → Category 2784 (Home & Garden > Decor > Home Fragrance Accessories > Candle Holders)
    "Candle Holders": "2784",           # Changed from 3309 to 2784
    "Candle Holder": "2784",            # Candle Holders
    "Candlestick": "2784",              # Candle Holders
    "Candelabra": "2784",               # Candle Holders (based on your assignments)
    
    # Candles → Category 588 (Home & Garden > Decor > Candles & Home Fragrances > Candles)
    "Candles": "588",                   # Changed from 3655 to 588
    "Candle": "588",                    # Candles
    "Taper Candle": "588",              # Candles
    "Dip Dye": "588",                   # Based on Dip Dye Candle assignment
    
    # Photo Frames → Category 4295 (Home & Garden > Decor > Picture Frames)
    "Photo Frame": "4295",              # Based on your Photo Frame assignments
    "Picture Frame": "4295",            # Picture Frames
    "Frame": "4295",                    # Picture Frames
    
    # Cushions → Category 4453 (Home & Garden > Decor > Throw Pillows)
    "Cushions": "4453",                 # Changed from 635 to 4453
    "Cushion": "4453",                  # Throw Pillows
    "Decorative Cushions": "4453",      # Throw Pillows
    
    # Wall Art → Category 500044 (Artwork - based on Comic Art assignment)
    "Wall Art": "500044",               # Changed from 639 to 500044
    "Artwork": "500044",                # Artwork
    "Comic Art": "500044",              # Based on your Comic Art assignment
    "Art": "500044",                    # Artwork
    
    # Decorative Items → Category 500045 (Figurines - based on Gorilla Gentleman assignment)
    "Decorative Accents": "500045",     # Changed from 632 to 500045
    "Figurines": "500045",              # Figurines
    "Decorative": "500045",             # Figurines
    "Sculpture": "500045",              # Figurines
    "Gentleman": "500045",              # Based on Gorilla Gentleman
    "Gorilla": "500045",                # Based on Gorilla Gentleman
    
    # Planters → Category 721 (Home & Garden > Lawn & Garden > Gardening > Planters & Pots)
    "Planter": "721",                   # Based on your Planter assignments
    "Planters": "721",                  # Planters & Pots
    
    # Storage & Organization → Category 7113 (Jars) or 6456 (Trays)
    "Jar": "7113",                      # Based on Lidded Jar assignment (changed from 594)
    "Lidded Jar": "7113",               # Storage Jars
    "Trinket Tray": "6456",             # Based on your Trinket Tray assignment
    "Tray": "6456",                     # Trays
    "Decorative Trays": "6456",         # Changed from 7097 to 6456
    
    # Ashtrays → Category 4009 (Home & Garden > Decor > Ashtrays)
    "Ashtray": "4009",                  # Based on your Ashtray assignment
    
    # ═══════════════════════════════════════════════════════════════
    # TABLE LINENS (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Table Linens → Various categories based on your assignments
    "Table Linens": "1985",             # Changed from 7458 to 1985 (Napkins)
    "Napkins": "1985",                  # Based on your Napkins assignment (changed from 7492)
    "Linen Napkins": "1985",            # Napkins
    "Placemats": "2547",                # Based on your Placemat assignment (changed from 7491)
    "Placemat": "2547",                 # Placemats
    "Linen Placemat": "2547",           # Placemats
    "Table Runners": "6325",            # Based on your Runner assignment (changed from 7494)
    "Runner": "6325",                   # Table Runners
    "Linen Runner": "6325",             # Table Runners
    "Table Cloths": "7493",             # Keep existing
    
    # ═══════════════════════════════════════════════════════════════
    # FURNITURE (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Tables → Category 5609 (Side Tables - based on David Bust assignment)
    "Side Tables": "5609",              # Changed from 6357 to 5609
    "Side Table": "5609",               # Side Tables
    "Coffee Tables": "6320",            # Keep existing
    "Console Tables": "6321",           # Keep existing
    "Table": "5609",                    # Default to Side Tables
    
    # ═══════════════════════════════════════════════════════════════
    # HOME FRAGRANCE (Based on your manual assignments)
    # ═══════════════════════════════════════════════════════════════
    
    # Home Fragrance → Category 4741 (based on Cello suite assignment)
    "Home Fragrance": "4741",           # Changed from 3654 to 4741
    "Diffusers": "4741",                # Changed from 5098 to 4741
    "Room Sprays": "5099",              # Keep existing
    "Fragrance": "4741",                # Home Fragrance
    "Cello": "4741",                    # Based on Cello suite assignment
    "Suite": "4741",                    # Based on Cello suite assignment
    
    # ═══════════════════════════════════════════════════════════════
    # SEASONAL & HOLIDAY DECOR
    # ═══════════════════════════════════════════════════════════════
    
    "Holiday": "3617",                  # Keep existing
    "Christmas": "5506",                # Keep existing
    "Ramadan": "3617",                  # Keep existing
    "Eid": "3617",                      # Keep existing
    "Special Occasion": "3617",         # Keep existing
    
    # ═══════════════════════════════════════════════════════════════
    # KITCHEN & COOKING
    # ═══════════════════════════════════════════════════════════════
    
    "Cookware": "672",                  # Keep existing
    "Bakeware": "673",                  # Keep existing
    
    # ═══════════════════════════════════════════════════════════════
    # GIFT ITEMS
    # ═══════════════════════════════════════════════════════════════
    
    "Gift": "5394",                     # Keep existing
    "Gift Box": "5424",                 # Keep existing
    
    # ═══════════════════════════════════════════════════════════════
    # BRAND-SPECIFIC MAPPINGS (Based on your data analysis)
    # ═══════════════════════════════════════════════════════════════
    
    # Brands mapped to their most common category in your Google Sheet data
    "BITOSSI": "3553",                  # Most BITOSSI products are plates (changed from 6208)
    "KERSTEN": "602",                   # Most KERSTEN products are vases (changed from 644)
    "KLIMCHI": "674",                   # Most KLIMCHI products are glassware (changed from 6228)
    "WERNS": "602",                     # Most WERNS products are vases (changed from 644)
    "ANNA + NINA": "6049",              # Most ANNA+NINA products are cups (changed from 6208)
    "EDION": "4741",                    # EDION products are home fragrance (changed from 632)
    "HOME STUDYO": "2784",              # HOME STUDYO products are candle holders
    "JOY&CO PICKS": "500045",           # JOY&CO PICKS are mostly decorative items
    "VAL POTTERY": "6049",              # VAL POTTERY are cups/mugs
    "SELETTI": "3330",                  # SELETTI products are serveware (changed from 632)
    "Joy & Co": "602",                  # Default to vases (changed from 166)
    
    # ═══════════════════════════════════════════════════════════════
    # OTHER CATEGORIES
    # ═══════════════════════════════════════════════════════════════
    
    "Accessories": "500045",            # Changed from 166 to 500045 (Figurines)
    "Home": "602",                      # Changed from 166 to 602 (Vases - most common)
    
    # ═══════════════════════════════════════════════════════════════
    # SPECIFIC PRODUCT KEYWORDS (Based on your product titles)
    # ═══════════════════════════════════════════════════════════════
    
    # Specific keywords found in your product titles
    "Abracadabra": "3553",              # BITOSSI Abracadabra products are mostly plates
    "Destino": "3553",                  # Destino plates
    "Incanto": "3553",                  # Incanto plates
    "Aurora": "602",                    # Aurora Vase
    "Azure": "602",                     # Azure Tower Vase
    "Birdy": "602",                     # Birdy Vase (also Birdy Bowl exists)
    "Emma": "2784",                     # Emma Candle Holder
    "Fancy": "6049",                    # Fancy Tea Cup Set
    "Good Morning": "6049",             # Good Morning Mug
    "Bisou": "4295",                    # Bisou Photo Frame
    "Ciao Bella": "4295",               # Ciao Bella Photo Frame
    "Je t'aime": "4295",                # Je t'aime Photo Frame
    "Retro": "4453",                    # Retro Cushions
    "Chrome Kiss": "721",               # Chrome Kiss Planter
    "David Bust": "5609",               # David Bust Side Table
    "Papillion": "7113",                # Papillion Lidded Jar
    "Classic": "7113",                  # Classic Lidded Jar
    "Sweetkeeper": "594",               # Sweetkeeper Jar (keep original)
    "Cozy": "2169",                     # Cozy Cappuccino Mug Set (keep original)
    "Chinoiserie": "6325",              # Chinoiserie Birds Runner
    "Palm Tree": "1985",                # Palm Tree Linen Napkins
    "Bronze Palm": "1985",              # Bronze Palm Trees products
}

# Default Google category - changed to most common category in your data
DEFAULT_GOOGLE_CATEGORY = "602"        # Home & Garden > Decor > Vases (most common in your data)

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

def map_to_google_category(category_name, title, brand):
    """
    Map Joy&Co category to Google's product taxonomy
    Using a multi-level approach checking category, title keywords, and brand
    UPDATED: Now uses your manual Google Sheet assignments as priority
    """
    # First try to match the exact category
    if category_name in CATEGORY_MAPPING:
        logging.info(f"Category match: '{category_name}' -> {CATEGORY_MAPPING[category_name]}")
        return CATEGORY_MAPPING[category_name]
        
    # Next, look for keywords in the category
    for keyword, google_id in CATEGORY_MAPPING.items():
        if keyword.lower() in category_name.lower():
            logging.info(f"Category keyword match: '{keyword}' in '{category_name}' -> {google_id}")
            return google_id
    
    # If category doesn't match, try to find keywords in the title
    title_lower = title.lower()
    for keyword, google_id in CATEGORY_MAPPING.items():
        if len(keyword) > 3 and keyword.lower() in title_lower:  # Avoid short words
            logging.info(f"Title keyword match: '{keyword}' in '{title}' -> {google_id}")
            return google_id
            
    # If still not found, check if we can map by brand
    if brand in CATEGORY_MAPPING:
        logging.info(f"Brand match: '{brand}' -> {CATEGORY_MAPPING[brand]}")
        return CATEGORY_MAPPING[brand]
    
    # Default fallback
    logging.info(f"Using default category for: '{title}' ({brand}) -> {DEFAULT_GOOGLE_CATEGORY}")
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
        
        # Fix the image_link extraction - use the actual product image instead of meta tag
        primary_image_element = soup.select_one(".cz-preview-item.active img.cz-image-zoom")
        if primary_image_element and 'src' in primary_image_element.attrs:
            image_link = primary_image_element['src']
        else:
            # Fallback to the first image if active not found
            image_element = soup.select_one(".cz-preview-item img.cz-image-zoom")
            image_link = image_element['src'] if image_element and 'src' in image_element.attrs else ""
        
        logging.info(f"Primary image extracted: {image_link}")
        
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
        image_elements = soup.select(".cz-preview-item img.cz-image-zoom")
        all_images = []
        for img in image_elements:
            if 'src' in img.attrs:
                if img['src'] not in all_images:  # Avoid duplicates
                    all_images.append(img['src'])
        
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
        
        # Map to Google product category using updated mapping
        google_product_category = map_to_google_category(category, title, brand)
        logging.info(f"Final Google category assignment: {google_product_category} for '{title}'")
        
        # Check if product is in stock
        stock_status = "in stock"
        out_of_stock_element = soup.select_one(".out-of-stock-label")
        if out_of_stock_element:
            stock_status = "out of stock"
        
        # Look for "Last X left" text to determine low inventory
        last_items_text = ""
        price_span = price_div.select_one("span.d-block") if price_div else None
        if price_span:
            last_items_text = price_span.get_text(strip=True)
            if "last" in last_items_text.lower() and "left" in last_items_text.lower():
                # Extract the number
                num_match = re.search(r'(\d+)', last_items_text)
                if num_match and int(num_match.group(1)) <= 3:
                    # Add a note about limited availability
                    stock_status = "limited availability"
            
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
        # Added additional_image_link to the standard CSV feed
        csv_fields = ["id", "title", "description", "link", "image_link", "additional_image_link",
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
    logging.info("Starting product feed generator with UPDATED category mappings")
    logging.info("=" * 80)
    logging.info("🔄 Using manual Google Sheet category assignments from June 26, 2025")
    logging.info("📊 Based on analysis of 242 products with preferred categorization")
    logging.info("=" * 80)
    
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
            logging.info(f"Debug - First product: {test_product['title']} -> Category: {test_product['google_product_category']}")
            
            # Create the standard feeds
            xml_success = generate_xml(products)
            csv_success = generate_csv(products)
            
            # Create the Google Merchant feed
            google_success = generate_google_merchant_feed(products)
            
            if csv_success and xml_success and google_success:
                print(f"✅ Successfully generated feeds for {len(products)} products.")
                print(f"📁 Files created:")
                print(f"   - {CSV_OUTPUT}")
                print(f"   - {XML_OUTPUT}") 
                print(f"   - {GOOGLE_MERCHANT_CSV}")
                print(f"🎯 Using UPDATED category mappings based on your manual assignments")
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
    main()
