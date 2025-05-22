import csv
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Generate Meta Shopping feed in CSV format
def generate_meta_csv_feed(products, output_file="meta_feed/facebook_product_feed.csv"):
    """
    Generate a Facebook/Meta product feed CSV file from product data
    """
    logging.info(f"Generating Meta Shopping CSV feed at {output_file} with {len(products)} products")
    
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
        "item_group_id"            # Optional: Group variants of the same product
    ]
    
    # Map Google categories to Facebook categories
    meta_products = map_products_for_meta(products)
    
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=meta_fields)
            writer.writeheader()
            
            for product in meta_products:
                writer.writerow(product)
        
        # Verify file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logging.info(f"Meta Shopping CSV feed successfully created at {output_file}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"Meta Shopping CSV feed was not created at {output_file}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating Meta Shopping CSV feed: {e}")
        return False

# Generate Meta Shopping feed in XML/RSS format
def generate_meta_xml_feed(products, output_file="meta_feed/facebook_product_feed.xml"):
    """
    Generate a Facebook/Meta product feed XML file from product data
    """
    logging.info(f"Generating Meta Shopping XML feed at {output_file} with {len(products)} products")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Map Google categories to Facebook categories
    meta_products = map_products_for_meta(products)
    
    try:
        # Create XML structure using RSS 2.0 format
        rss = ET.Element("rss")
        rss.set("version", "2.0")
        rss.set("xmlns:g", "http://base.google.com/ns/1.0")
        
        channel = ET.SubElement(rss, "channel")
        
        # Add feed metadata
        title = ET.SubElement(channel, "title")
        title.text = "Joy&Co Product Feed for Meta Shopping"
        
        description = ET.SubElement(channel, "description")
        description.text = "Product feed for Joy&Co products compatible with Meta Shopping"
        
        link = ET.SubElement(channel, "link")
        link.text = "https://joyandco.com"
        
        # Add current date and time
        pubDate = ET.SubElement(channel, "pubDate")
        pubDate.text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Add products
        for product in meta_products:
            item = ET.SubElement(channel, "item")
            
            # Add required fields
            for field in ["id", "title", "description", "link"]:
                element = ET.SubElement(item, "g:" + field)
                element.text = product.get(field, "")
            
            # Add price
            price_elem = ET.SubElement(item, "g:price")
            price_elem.text = product.get("price", "")
            
            # Add sale price if available
            if product.get("sale_price"):
                sale_price_elem = ET.SubElement(item, "g:sale_price")
                sale_price_elem.text = product.get("sale_price", "")
            
            # Add image link
            image_link = ET.SubElement(item, "g:image_link")
            image_link.text = product.get("image_link", "")
            
            # Add additional image link if available
            if product.get("additional_image_link"):
                additional_image = ET.SubElement(item, "g:additional_image_link")
                additional_image.text = product.get("additional_image_link", "")
            
            # Add brand
            brand = ET.SubElement(item, "g:brand")
            brand.text = product.get("brand", "")
            
            # Add availability
            availability = ET.SubElement(item, "g:availability")
            availability.text = product.get("availability", "")
            
            # Add condition
            condition = ET.SubElement(item, "g:condition")
            condition.text = product.get("condition", "")
            
            # Add Google product category if available
            if product.get("google_product_category"):
                g_category = ET.SubElement(item, "g:google_product_category")
                g_category.text = product.get("google_product_category", "")
                
            # Add Facebook product category if available
            if product.get("fb_product_category"):
                fb_category = ET.SubElement(item, "g:fb_product_category")
                fb_category.text = product.get("fb_product_category", "")
                
            # Add inventory if available
            if product.get("inventory"):
                inventory = ET.SubElement(item, "g:inventory")
                inventory.text = product.get("inventory", "")
                
            # Add item_group_id if available
            if product.get("item_group_id"):
                item_group = ET.SubElement(item, "g:item_group_id")
                item_group.text = product.get("item_group_id", "")
        
        # Convert to string with pretty formatting
        rough_string = ET.tostring(rss, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        # Verify file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logging.info(f"Meta Shopping XML feed successfully created at {output_file}, size: {file_size} bytes")
            return True
        else:
            logging.error(f"Meta Shopping XML feed was not created at {output_file}")
            return False
            
    except Exception as e:
        logging.error(f"Error generating Meta Shopping XML feed: {e}")
        return False

# Map products to Meta format
def map_products_for_meta(products):
    """
    Map product data to Meta Shopping format
    """
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
    
    meta_products = []
    
    for product in products:
        # Map product data to Meta Shopping format
        meta_product = {
            "id": product.get("id", ""),
            "title": product.get("title", ""),
            "description": product.get("description", ""),
            "availability": availability_mapping.get(product.get("availability", ""), "in stock"),
            "condition": product.get("condition", "new"),
            "price": product.get("price", ""),
            "link": product.get("link", ""),
            "image_link": product.get("image_link", ""),
            "brand": product.get("brand", ""),
            "additional_image_link": product.get("additional_image_link", ""),
            "google_product_category": product.get("google_product_category", ""),
            "fb_product_category": fb_category_mapping.get(product.get("google_product_category", ""), ""),
            "item_group_id": product.get("item_group_id", "")
        }
        
        # Add sale price if available
        if product.get("has_sale") and product.get("sale_price"):
            meta_product["sale_price"] = product.get("sale_price", "")
        else:
            meta_product["sale_price"] = ""
        
        # Add inventory field (not available in current data)
        meta_product["inventory"] = ""
        
        meta_products.append(meta_product)
        
    return meta_products

# Main function to generate both CSV and XML feeds
def main():
    logging.info("Starting Meta Shopping feed generator")
    
    # Path to existing XML product feed
    XML_INPUT = "google_feed/product_feed.xml"
    META_CSV_OUTPUT = "meta_feed/facebook_product_feed.csv"
    META_XML_OUTPUT = "meta_feed/facebook_product_feed.xml"
    
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
        
        # Generate Meta Shopping feeds
        csv_success = generate_meta_csv_feed(products, META_CSV_OUTPUT)
        xml_success = generate_meta_xml_feed(products, META_XML_OUTPUT)
        
        if csv_success and xml_success:
            print(f"✅ Successfully generated Meta Shopping feeds with {len(products)} products")
            print(f"   - CSV feed: {META_CSV_OUTPUT}")
            print(f"   - XML feed: {META_XML_OUTPUT}")
        else:
            if not csv_success:
                print(f"❌ Failed to generate Meta Shopping CSV feed")
            if not xml_success:
                print(f"❌ Failed to generate Meta Shopping XML feed")
            
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
