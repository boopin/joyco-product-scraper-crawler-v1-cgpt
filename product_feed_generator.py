import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read URLs from crawler output
INPUT_CSV = "product_urls/product_links.csv"
CSV_OUTPUT = "google_feed/product_feed.csv"
XML_OUTPUT = "google_feed/product_feed.xml"

# Ensure output directory exists
os.makedirs("google_feed", exist_ok=True)
logging.info(f"Ensured google_feed directory exists")

def extract_product_data(url):
    try:
        logging.info(f"Extracting data from: {url}")
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product ID from URL
        product_id = url.split("/")[-1]
        
        # Get title from the product detail h2 - fixed selector for better targeting
        title_tag = soup.select_one(".col-md-6 h2")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        logging.info(f"Title extracted: {title}")
        
        # Get full description from class="text-body" div in #description
        description_div = soup.select_one("#description .text-body")
        description = description_div.get_text(strip=True) if description_div else "No Description"
        logging.info(f"Description extracted: {len(description)} characters")
        
        # Get image link from meta tag
        image_tag = soup.find("meta", property="og:image")
        image_link = image_tag['content'] if image_tag else ""
        
        # Get price from the .price div (removes currency code)
        price_div = soup.select_one(".price")
        price = "0.00"
        if price_div:
            price_text = price_div.get_text(strip=True)
            # Extract numeric price
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_text)
            if price_match:
                price = price_match.group(1)
        logging.info(f"Price extracted: {price}")
        
        # Get brand from the p.pic-info
        brand_tag = soup.select_one("p.pic-info")
        brand = brand_tag.get_text(strip=True) if brand_tag else "Joy & Co"
        logging.info(f"Brand extracted: {brand}")

        product_data = {
            "id": product_id,
            "title": title,
            "description": description,
            "link": url,
            "image_link": image_link,
            "availability": "in stock",
            "price": f"{price} AED",
            "brand": brand,
            "condition": "new"
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
        
        # Convert all values to strings for CSV compatibility
        string_products = []
        for product in products:
            string_product = {k: str(v) if v is not None else "" for k, v in product.items()}
            string_products.append(string_product)
        
        with open(CSV_OUTPUT, mode='w', newline='', encoding='utf-8') as file:
            if not products:
                logging.warning("No products to write to CSV")
                return False
                
            writer = csv.DictWriter(file, fieldnames=products[0].keys())
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

def generate_xml(products):
    try:
        logging.info(f"Generating XML at {XML_OUTPUT} with {len(products)} products")
        
        root = ET.Element("products")
        for p in products:
            product = ET.SubElement(root, "product")
            for k, v in p.items():
                el = ET.SubElement(product, k)
                # Explicitly convert value to string if not None
                el.text = str(v) if v is not None else ""
        
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
            logging.info(f"Debug - First product: {test_product}")
            
            # First try to create just the XML file to confirm parsing works
            xml_success = generate_xml(products)
            logging.info(f"XML generation: {'Success' if xml_success else 'Failed'}")
            
            # Then try CSV generation
            csv_success = generate_csv(products)
            logging.info(f"CSV generation: {'Success' if csv_success else 'Failed'}")
            
            if csv_success and xml_success:
                print(f"✅ Successfully generated feed for {len(products)} products.")
            elif csv_success:
                print(f"⚠️ Generated CSV only for {len(products)} products. XML failed.")
            elif xml_success:
                print(f"⚠️ Generated XML only for {len(products)} products. CSV failed.")
            else:
                print("❌ Failed to generate both CSV and XML feeds.")
        else:
            logging.warning("No products were processed.")
            print("⚠️ No products were processed.")
            
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
