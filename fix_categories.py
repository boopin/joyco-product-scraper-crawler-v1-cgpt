import os
import sys
import pandas as pd
import logging

# Configure logging to both console and file
LOG_FILE = "fix_categories.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Formatter for logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
logger.addHandler(ch)

# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setFormatter(formatter)
logger.addHandler(fh)

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')           # Original feed CSV
MAPPING_FILE = os.getenv('MAPPING_FILE', 'category_suggestions.csv')                  # Invalid-to-valid category map CSV
TAXONOMY_FILE = os.getenv('TAXONOMY_FILE', 'google_product_taxonomy.txt')              # Official taxonomy file from Google
OUTPUT_FIXED_FEED = os.getenv('OUTPUT_FIXED_FEED', 'google_feed/google_merchant_feed_fixed.csv')  # Output fixed feed CSV
OUTPUT_UNMATCHED = os.getenv('OUTPUT_UNMATCHED', 'unmatched_invalid_categories.csv')   # Unmatched invalid categories CSV

def check_file_exists(filepath):
    if not os.path.isfile(filepath):
        logger.error(f"❌ File not found: {filepath}")
        sys.exit(1)

def load_taxonomy(taxonomy_file):
    check_file_exists(taxonomy_file)
    try:
        df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
        taxonomy_ids = set(df['category_id'].astype(str).str.strip())
        logger.info(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories from {taxonomy_file}")
        return taxonomy_ids
    except Exception as e:
        logger.error(f"❌ Error loading taxonomy file: {e}")
        sys.exit(1)

def load_mapping(mapping_file):
    check_file_exists(mapping_file)
    try:
        df = pd.read_csv(mapping_file, dtype=str)
        required_cols = ['Invalid Category ID', 'Suggested Category ID']
        for col in required_cols:
            if col not in df.columns:
                logger.error(f"❌ Column '{col}' missing in mapping CSV!")
                sys.exit(1)
        mapping_dict = dict(zip(df['Invalid Category ID'].str.strip(), df['Suggested Category ID'].str.strip()))
        logger.info(f"✅ Loaded {len(mapping_dict)} mappings from {mapping_file}")
        return mapping_dict
    except Exception as e:
        logger.error(f"❌ Error loading mapping file: {e}")
        sys.exit(1)

def fix_categories(feed_file, mapping_dict, taxonomy_ids):
    check_file_exists(feed_file)
    try:
        feed_df = pd.read_csv(feed_file, dtype=str)
        if 'google_product_category' not in feed_df.columns:
            logger.error("❌ Column 'google_product_category' not found in feed file!")
            sys.exit(1)

        # Clean category column
        feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

        # Find unmatched invalid categories before fix
        unmatched_before_fix = feed_df[~feed_df['google_product_category'].isin(taxonomy_ids)]['google_product_category'].drop_duplicates()
        logger.info(f"ℹ️ Found {len(unmatched_before_fix)} unmatched invalid categories before fix.")

        # AUTO-MAPPING FOR UNMATCHED CATEGORIES
        unmatched_to_map = [cat for cat in unmatched_before_fix if cat not in mapping_dict]

        if unmatched_to_map:
            logger.info(f"⚠️ Found {len(unmatched_to_map)} unmatched categories without mapping. Attempting auto-mapping...")
            # Use simple heuristic: map to closest taxonomy ID by numeric similarity (nearest neighbor)
            for invalid_cat in unmatched_to_map:
                try:
                    invalid_num = int(invalid_cat)
                    # Find taxonomy id with minimal absolute difference
                    closest_tax = min(taxonomy_ids, key=lambda x: abs(int(x) - invalid_num))
                    mapping_dict[invalid_cat] = closest_tax
                    logger.info(f"Auto-mapped invalid category {invalid_cat} to {closest_tax}")
                except Exception as e:
                    logger.warning(f"Could not auto-map invalid category {invalid_cat}: {e}")

        # Map invalid categories to suggested valid categories
        feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(
            lambda x: mapping_dict.get(x, x)
        )

        # Find invalid categories after applying mapping
        invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]

        # Prepare unmatched invalid categories report
        unmatched = invalid_after_fix['google_product_category_fixed'].drop_duplicates().reset_index(drop=True)
        unmatched.to_frame(name='Unmatched Invalid Category').to_csv(OUTPUT_UNMATCHED, index=False)

        # Replace original categories with fixed categories
        feed_df['google_product_category'] = feed_df['google_product_category_fixed']
        feed_df.drop(columns=['google_product_category_fixed'], inplace=True)

        # Save fixed feed CSV
        feed_df.to_csv(OUTPUT_FIXED_FEED, index=False)

        logger.info(f"✅ Fixed feed saved to: {OUTPUT_FIXED_FEED}")
        logger.info(f"✅ Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
        logger.info(f"ℹ️ Total unmatched invalid categories after fix: {len(unmatched)}")

    except Exception as e:
        logger.error(f"❌ Error processing feed file: {e}")
        sys.exit(1)

def main():
    taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
    mapping_dict = load_mapping(MAPPING_FILE)
    fix_categories(FEED_FILE, mapping_dict, taxonomy_ids)

if __name__ == "__main__":
    main()
