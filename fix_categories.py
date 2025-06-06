import os
import sys
import pandas as pd
import logging
from rapidfuzz import process, fuzz  # rapidfuzz is faster alternative to fuzzywuzzy

# Setup logging to file and stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_categories.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')
MAPPING_FILE = os.getenv('MAPPING_FILE', 'category_suggestions.csv')
TAXONOMY_FILE = os.getenv('TAXONOMY_FILE', 'google_product_taxonomy.txt')
OUTPUT_FIXED_FEED = os.getenv('OUTPUT_FIXED_FEED', 'google_feed/google_merchant_feed_fixed.csv')
OUTPUT_UNMATCHED = os.getenv('OUTPUT_UNMATCHED', 'unmatched_invalid_categories.csv')

def check_file_exists(filepath):
    if not os.path.isfile(filepath):
        logger.error(f"❌ File not found: {filepath}")
        sys.exit(1)

def load_taxonomy(taxonomy_file):
    check_file_exists(taxonomy_file)
    try:
        df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
        df['category_id'] = df['category_id'].astype(str).str.strip()
        df['category_name'] = df['category_name'].astype(str).str.strip()
        taxonomy_ids = set(df['category_id'])
        taxonomy_names = df.set_index('category_id')['category_name'].to_dict()
        logger.info(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories from {taxonomy_file}")
        return taxonomy_ids, taxonomy_names
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

def extract_category_id(cat_string):
    """
    Extract numeric category ID from a string like:
    "6543 - Home & Garden > Kitchen & Dining > Kitchen Appliances > Hot Drink Makers"
    Returns the numeric string ID or None if parsing fails.
    """
    try:
        if pd.isna(cat_string):
            return None
        first_part = cat_string.split(' ')[0]
        first_part = first_part.strip('-').strip()
        if first_part.isdigit():
            return first_part
        else:
            first_part = cat_string.split('-')[0].strip()
            if first_part.isdigit():
                return first_part
        return None
    except Exception as e:
        logger.warning(f"Failed to extract category ID from '{cat_string}': {e}")
        return None

def find_best_fuzzy_match(invalid_cat, taxonomy_names):
    """
    Use rapidfuzz to find the best matching taxonomy category name for the invalid category.
    Returns (best_id, best_name, score) or (None, None, 0) if no good match found.
    """
    try:
        # rapidfuzz process.extractOne returns (match_name, score, key)
        # We want to match against taxonomy_names.values()
        best_match = process.extractOne(
            invalid_cat,
            taxonomy_names.values(),
            scorer=fuzz.token_sort_ratio,
            score_cutoff=60  # Only accept matches with 60+ similarity
        )
        if best_match:
            best_name, score, _ = best_match
            # Find corresponding category_id by name
            for cat_id, cat_name in taxonomy_names.items():
                if cat_name == best_name:
                    return cat_id, cat_name, score
        return None, None, 0
    except Exception as e:
        logger.warning(f"Fuzzy match failed for '{invalid_cat}': {e}")
        return None, None, 0

def fix_categories(feed_file, mapping_dict, taxonomy_ids, taxonomy_names):
    check_file_exists(feed_file)
    try:
        feed_df = pd.read_csv(feed_file, dtype=str)
        if 'google_product_category' not in feed_df.columns:
            logger.error("❌ Column 'google_product_category' not found in feed file!")
            sys.exit(1)

        feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

        # Find unmatched invalid categories (not in taxonomy or mapping)
        unmatched_invalid_categories = set()
        for cat in set(feed_df['google_product_category'].unique()):
            if cat not in taxonomy_ids and cat not in mapping_dict:
                unmatched_invalid_categories.add(cat)

        if unmatched_invalid_categories:
            logger.info(f"⚠️ Found {len(unmatched_invalid_categories)} unmatched categories without mapping. Attempting fuzzy auto-mapping...")

            for invalid_cat in unmatched_invalid_categories:
                best_id, best_name, score = find_best_fuzzy_match(invalid_cat, taxonomy_names)
                if best_id:
                    mapping_dict[invalid_cat] = best_id
                    logger.info(f"Auto-mapped '{invalid_cat}' to '{best_name}' ({best_id}) with similarity {score}%")
                else:
                    # Fallback ID if no match found
                    fallback_category_id = '6543'  # Change as needed
                    mapping_dict[invalid_cat] = fallback_category_id
                    logger.warning(f"No good fuzzy match found for '{invalid_cat}'. Assigned fallback category ID {fallback_category_id}")

        # Map categories with extracted numeric IDs
        def map_category(cat):
            if cat in mapping_dict:
                suggested = mapping_dict[cat]
                extracted_id = extract_category_id(suggested)
                if extracted_id and extracted_id in taxonomy_ids:
                    return extracted_id
                else:
                    # Sometimes mapping might be direct ID string already
                    if suggested in taxonomy_ids:
                        return suggested
                    logger.warning(f"Could not extract valid numeric ID for mapping '{suggested}' from invalid category '{cat}'. Using original category.")
                    return cat
            else:
                return cat

        feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(map_category)

        invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]

        unmatched = invalid_after_fix['google_product_category_fixed'].drop_duplicates().reset_index(drop=True)
        unmatched.to_frame(name='Unmatched Invalid Category').to_csv(OUTPUT_UNMATCHED, index=False)

        feed_df['google_product_category'] = feed_df['google_product_category_fixed']
        feed_df.drop(columns=['google_product_category_fixed'], inplace=True)

        feed_df.to_csv(OUTPUT_FIXED_FEED, index=False)

        logger.info(f"✅ Fixed feed saved to: {OUTPUT_FIXED_FEED}")
        logger.info(f"✅ Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
        logger.info(f"ℹ️ Total unmatched invalid categories after fix: {len(unmatched)}")

    except Exception as e:
        logger.error(f"❌ Error processing feed file: {e}")
        sys.exit(1)

def main():
    taxonomy_ids, taxonomy_names = load_taxonomy(TAXONOMY_FILE)
    mapping_dict = load_mapping(MAPPING_FILE)
    fix_categories(FEED_FILE, mapping_dict, taxonomy_ids, taxonomy_names)

if __name__ == "__main__":
    main()
