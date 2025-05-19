import requests
from bs4 import BeautifulSoup
import csv
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
import os
import logging

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
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No Title"
        description = soup.find("meta", attrs={"name": "description"})
        description = description['content'].strip() if description else "No Description"
        image_tag = soup.find("meta", property="og:image")
        image_link = image_tag['content'] if image_tag else ""
        price = soup.find("meta", attrs={"itemprop": "price"})
        price = price['content'] if price else "0.00"

        product_data = {
            "id": url.split("/")[-1],
            "title": title,
            "description": description,
            "link": url,
            "image_link": image_link,
            "availability": "in stock",
            "price": f"{price} AED",
            "brand": "Joy & Co",
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
            csv_success = generate_csv(products)
            xml_success = generate_xml(products)
            
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
