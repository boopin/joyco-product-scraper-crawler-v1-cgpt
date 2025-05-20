import csv
import os
import logging
import json
from datetime import datetime

# Function to generate Meta Shopping feed from existing product data
def generate_meta_shopping_feed(products, output_file="meta_feed/facebook_product_feed.csv"):
    """
    Generate a Facebook/Meta product feed CSV file from product data
    """
    logging.info(f"Generating Meta Shopping feed at {output_file} with {len(products)} products")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Define Meta Shopping Feed fields
    # Reference: https://www.facebook.com/business/help/120325381656392
    meta_fields = [
        "id",                      # Required: A unique identifier for the item
        "title",                   # Required: The name of the item
        "description",             # Required: Description of the item
        "availability",            # Required: In stock, out of stock, preorder, available for order
        "condition",               # Required: new, refurbished, used
        "price",                   # Required: The price of the item
        "link",                    # Required: The URL to the product page
        "image_link",              # Required: The URL for the product's main image
        "brand",                   # Required: The brand name of the product
        "additional_image_link",   # Optional: Additional product images
        "google_product_category", # Optional: Google product taxonomy
        "fb_product_category",     # Optional: Facebook product category
        "sale_price",              # Optional: Sale price
        "inventory",               # Optional: Number of items in stock
    ]
    
    # Map availability to Meta format
    availability_mapping = {
        "in stock": "in stock",
        "out of stock": "out of stock",
        "limited availability": "in stock"
    }
    
    # Map Google categories to Facebook categories (simplified)
    # For a complete mapping, see: https://www.facebook.com/business/help/1244435349304218
    fb_category_mapping = {
        # Home & Garden
        "166": "home_goods", # Home & Garden > Decor
        "632": "home_goods", # Decorative Accents
        "635": "home_goods", # Throw Pillows
        "639": "home_goods", # Artwork
        "644": "home_goods", # Vases
        "3654": "home_goods", # Candles & Home Fragrances
        "3655": "home_goods", # Candles
        "3309": "home_goods", # Candleholders
        "7097": "home_goods", # Decorative Trays
        "3617": "seasonal_holiday_supplies", # Seasonal & Holiday Decorations
        "5506": "seasonal_holiday_supplies", # Christmas Decorations
        
        # Kitchen & Dining
        "6208": "household_supplies", # Tableware
        "6209": "household_supplies", # Bowls
        "6210": "household_supplies", # Plates
        "728": "household_supplies",  # Cutlery
        "6228": "household_supplies", # Glasses & Tumblers
        "6231": "household_supplies", # Cups & Mugs
        "734": "household_supplies",  # Serving Trays & Platters
        "672": "household_supplies",  # Cookware
        "673": "household_supplies",  # Bakeware
        "7458": "household_supplies", # Table Linens
        "7491": "household_supplies", # Placemats
        "7492": "household_supplies", # Napkins
        "7493": "household_supplies", # Tablecloths
        "7494": "household_supplies", # Table Runners
        
        # Furniture
        "6320": "furniture", # Coffee Tables
        "6321": "furniture", # Console Tables
        "6357": "furniture", # Side Tables
        
        # Gifts
        "5394": "gift_giving", # Gift Giving
        "5424": "gift_giving"  # Gift Sets
    }
    
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=meta_fields)
            writer.writeheader()
            
            for product in products:
                # Map product data to Meta Shopping format
                meta_product = {
                    "id": product["id"],
                    "title": product["title"],
                    "description": product["description"],
                    "availability": availability_mapping.get(product["availability"], "in stock"),
                    "condition": product["condition"],
                    "price": product["price"],
                    "link": product["link"],
                    "image_link": product["image_link"],
                    "brand": product["brand"],
                    "additional_image_link": product.get("additional_image_link", ""),
                    "google_product_category": product.get("google_product_category", ""),
                    "fb_product_category": fb_category_mapping.get(product.get("google_product_category", ""), ""),
                    "sale_price": "",  # Not available in current data
                    "inventory": ""    # Not available in current data
                }
                
                writer.writerow(meta_product)
        
        # Verify file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logging.info(f"Meta Shopping feed successfully created at {output_file}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"Meta Shopping feed was not created at {output_file}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating Meta Shopping feed: {e}")
        return False

# If this script is run directly, load product data from XML feed and generate Meta feed
if __name__ == "__main__":
    import xml.etree.ElementTree as ET
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("Starting Meta Shopping feed generator")
    
    # Path to existing XML product feed
    XML_INPUT = "google_feed/product_feed.xml"
    META_OUTPUT = "meta_feed/facebook_product_feed.csv"
    
    try:
        if not os.path.exists(XML_INPUT):
            logging.error(f"Input XML file does not exist: {XML_INPUT}")
            sys.exit(1)
            
        # Load products from XML feed
        tree = ET.parse(XML_INPUT)
        root = tree.getroot()
        
        products = []
        for product_elem in root.findall('product'):
            product = {}
            for elem in product_elem:
                if elem.tag not in ['additional_images', 'variants']:
                    product[elem.tag] = elem.text or ""
            products.append(product)
            
        logging.info(f"Loaded {len(products)} products from XML feed")
        
        # Generate Meta Shopping feed
        success = generate_meta_shopping_feed(products, META_OUTPUT)
        
        if success:
            print(f"✅ Successfully generated Meta Shopping feed with {len(products)} products")
        else:
            print(f"❌ Failed to generate Meta Shopping feed")
            
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
