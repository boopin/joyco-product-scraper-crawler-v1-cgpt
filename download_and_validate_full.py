import os
import sys
import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')
TAXONOMY_FILE = os.getenv('TAXONOMY_FILE', 'google_product_taxonomy.txt')
VALIDATION_REPORT = 'category_validation_full_report.csv'

def download_taxonomy(taxonomy_file):
    url = "https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt"
    try:
        logger.info("Downloading Google product taxonomy...")
        r = requests.get(url)
        r.raise_for_status()
        with open(taxonomy_file, 'w', encoding='utf-8') as f:
            f.write(r.text)
        logger.info(f"✅ Taxonomy saved to {taxonomy_file}")
    except Exception as e:
        logger.error(f"❌ Error downloading taxonomy: {e}")
        sys.exit(1)

def load_taxonomy_ids(taxonomy_file):
    if not os.path.isfile(taxonomy_file):
        logger.error(f"❌ Taxonomy file not found: {taxonomy_file}")
        sys.exit(1)
    df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
    taxonomy_ids = set(df['category_id'].astype(str).str.strip())
    logger.info(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories")
    return taxonomy_ids

def validate_categories(feed_file, taxonomy_ids):
    if not os.path.isfile(feed_file):
        logger.error(f"❌ Feed file not found: {feed_file}")
        sys.exit(1)
    feed_df = pd.read_csv(feed_file, dtype=str)
    feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

    feed_df['is_category_valid'] = feed_df['google_product_category'].isin(taxonomy_ids)
    invalid_count = (~feed_df['is_category_valid']).sum()

    logger.info(f"Total products checked: {len(feed_df)}")
    logger.info(f"Invalid category count: {invalid_count}")

    feed_df.to_csv(VALIDATION_REPORT, index=False)
    logger.info(f"Full validation report saved as: {VALIDATION_REPORT}")

    return feed_df

def main():
    download_taxonomy(TAXONOMY_FILE)
    taxonomy_ids = load_taxonomy_ids(TAXONOMY_FILE)
    validate_categories(FEED_FILE, taxonomy_ids)

if __name__ == "__main__":
    main()
