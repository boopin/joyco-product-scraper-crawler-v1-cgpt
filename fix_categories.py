import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')
MAPPING_FILE = 'category_suggestions.csv'
TAXONOMY_FILE = 'google_product_taxonomy.txt'
OUTPUT_FIXED_FEED = 'google_merchant_feed_fixed.csv'
OUTPUT_UNMATCHED = 'unmatched_invalid_categories.csv'

def load_taxonomy(taxonomy_file):
    df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
    taxonomy_ids = set(df['category_id'].astype(str).str.strip())
    logger.info(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories")
    return taxonomy_ids

def load_mapping(mapping_file):
    df = pd.read_csv(mapping_file, dtype=str)
    required_columns = ['Invalid Category ID', 'Suggested Category ID']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in mapping file")
    mapping_dict = dict(zip(df['Invalid Category ID'].str.strip(), df['Suggested Category ID'].str.strip()))
    logger.info(f"✅ Loaded {len(mapping_dict)} category mappings")
    return mapping_dict

def fix_categories(feed_file, mapping_dict, taxonomy_ids):
    logger.info(f"Loading feed from {feed_file}")
    feed_df = pd.read_csv(feed_file, dtype=str)
    feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

    # Apply mappings to replace invalid categories
    feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(
        lambda x: mapping_dict.get(x, x)
    )

    # Identify invalid categories after applying mapping
    invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]

    unmatched = invalid_after_fix['google_product_category_fixed'].drop_duplicates().reset_index(drop=True)
    unmatched.to_frame(name='Unmatched Invalid Category').to_csv(OUTPUT_UNMATCHED, index=False)

    # Replace original categories with fixed categories
    feed_df['google_product_category'] = feed_df['google_product_category_fixed']
    feed_df.drop(columns=['google_product_category_fixed'], inplace=True)

    feed_df.to_csv(OUTPUT_FIXED_FEED, index=False)

    logger.info(f"✅ Fixed feed saved to: {OUTPUT_FIXED_FEED}")
    logger.info(f"✅ Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
    logger.info(f"ℹ️ Total unmatched invalid categories: {len(unmatched)}")

def main():
    try:
        taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
        mapping_dict = load_mapping(MAPPING_FILE)
        fix_categories(FEED_FILE, mapping_dict, taxonomy_ids)
    except Exception as e:
        logger.error(f"Category fixing failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
