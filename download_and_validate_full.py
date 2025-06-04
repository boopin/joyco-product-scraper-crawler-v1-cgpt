import os
import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')
TAXONOMY_URL = 'https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt'
TAXONOMY_FILE = 'google_product_taxonomy.txt'
REPORT_FILE = 'category_validation_full_report.csv'

def download_taxonomy():
    logger.info("Downloading Google product taxonomy...")
    response = requests.get(TAXONOMY_URL)
    response.raise_for_status()
    with open(TAXONOMY_FILE, 'wb') as f:
        f.write(response.content)
    logger.info(f"✅ Taxonomy saved to {TAXONOMY_FILE}")

def load_taxonomy():
    df = pd.read_csv(TAXONOMY_FILE, sep='\t', header=None, names=['category_id', 'category_name'])
    taxonomy_ids = set(df['category_id'].astype(str).str.strip())
    logger.info(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories")
    return taxonomy_ids

def validate_categories(feed_file, taxonomy_ids):
    logger.info(f"Validating product categories in feed: {feed_file}")
    feed_df = pd.read_csv(feed_file, dtype=str)
    feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()
    feed_df['is_valid_category'] = feed_df['google_product_category'].isin(taxonomy_ids)
    
    total = len(feed_df)
    invalid_count = (~feed_df['is_valid_category']).sum()
    logger.info(f"Total products checked: {total}")
    logger.info(f"Invalid category count: {invalid_count}")
    
    feed_df.to_csv(REPORT_FILE, index=False)
    logger.info(f"Full validation report saved as: {REPORT_FILE}")
    return feed_df

def main():
    try:
        download_taxonomy()
        taxonomy_ids = load_taxonomy()
        validate_categories(FEED_FILE, taxonomy_ids)
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
