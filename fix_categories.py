import os
import sys
import re
import pandas as pd
import logging
from rapidfuzz import process, fuzz

FEED_FILE = os.getenv('FEED_FILE', 'google_feed/google_merchant_feed.csv')           # Original feed CSV
MAPPING_FILE = os.getenv('MAPPING_FILE', 'category_suggestions.csv')                  # Invalid-to-valid category map CSV
TAXONOMY_FILE = os.getenv('TAXONOMY_FILE', 'google_product_taxonomy.txt')              # Official taxonomy file from Google
OUTPUT_FIXED_FEED = os.getenv('OUTPUT_FIXED_FEED', 'google_feed/google_merchant_feed_fixed.csv')  # Output fixed feed CSV
OUTPUT_UNMATCHED = os.getenv('OUTPUT_UNMATCHED', 'unmatched_invalid_categories.csv')   # Unmatched invalid categories CSV
LOG_FILE = 'fix_categories.log'

# Configure logging to file and console with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

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

def extract_numeric_category_id(cat_str):
    """
    Extract numeric category ID from string like '6543 - Some Category Name'
    Returns the numeric part as string, or None if not found.
    """
    if isinstance(cat_str, str):
        match = re.match(r'^(\d+)', cat_str.strip())
        if match:
            return match.group(1)
    return None

def fix_categories(feed_file, mapping_dict, taxonomy_ids):
    check_file_exists(feed_file)
    try:
        feed_df = pd.read_csv(feed_file, dtype=str)
        if 'google_product_category' not in feed_df.columns:
            logger.error("❌ Column 'google_product_category' not found in feed file!")
            sys.exit(1)

        # Clean category column
        feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

        # Map invalid categories to suggested valid categories using existing mapping
        feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(
            lambda x: mapping_dict.get(x, x)
        )

        # Identify invalid categories after applying current mapping
        invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]

        unmatched_invalid_categories = set(invalid_after_fix['google_product_category_fixed'].unique())

        if unmatched_invalid_categories:
            logger.warning(f"⚠️ Found {len(unmatched_invalid_categories)} unmatched categories without mapping. Attempting fuzzy auto-mapping...")

            # Prepare list of valid taxonomy categories as strings
            valid_categories = list(taxonomy_ids)

            fallback_category_id = "6543"  # Fallback numeric ID only

            for invalid_cat in unmatched_invalid_categories:
                # Use rapidfuzz to find best fuzzy match among taxonomy categories by category name only
                # Extract just category names from taxonomy to improve fuzzy matching
                # Taxonomy is 'id - name' or just 'id', so split once
                def get_name(cat):
                    parts = cat.split(' - ', 1)
                    return parts[1] if len(parts) > 1 else ''

                # Prepare choices dict id -> name
                choices = {cat_id: get_name(cat_id) for cat_id in valid_categories}

                # Get best match by fuzzy ratio on category names
                best_match = None
                best_score = 0

                for cat_id, name in choices.items():
                    score = fuzz.ratio(invalid_cat, cat_id)  # fuzzy ratio on full invalid_cat vs id? probably low
                    score_name = fuzz.ratio(invalid_cat, name)  # fuzzy ratio on invalid_cat vs taxonomy category name
                    max_score = max(score, score_name)
                    if max_score > best_score:
                        best_score = max_score
                        best_match = cat_id

                # Threshold for accepting a match, e.g. 60%
                if best_score >= 60:
                    # Use just the numeric part of best_match
                    numeric_id = extract_numeric_category_id(best_match)
                    if numeric_id:
                        mapping_dict[invalid_cat] = numeric_id
                        logger.info(f"✅ Auto-mapped invalid category '{invalid_cat}' to '{numeric_id}' with score {best_score}")
                    else:
                        mapping_dict[invalid_cat] = fallback_category_id
                        logger.warning(f"Could not extract numeric ID from best match '{best_match}' for invalid category '{invalid_cat}'. Assigned fallback ID {fallback_category_id}")
                else:
                    mapping_dict[invalid_cat] = fallback_category_id
                    logger.warning(f"No good fuzzy match found for '{invalid_cat}'. Assigned fallback category ID {fallback_category_id}")

            # Re-apply mapping after auto-mapping additions
            feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(
                lambda x: mapping_dict.get(x, x)
            )

            # Recompute invalid after fix
            invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]
            unmatched_invalid_categories = set(invalid_after_fix['google_product_category_fixed'].unique())

        # Prepare unmatched invalid categories report CSV
        unmatched = pd.Series(list(unmatched_invalid_categories))
        unmatched.to_frame(name='Unmatched Invalid Category').to_csv(OUTPUT_UNMATCHED, index=False)

        # Replace original categories with fixed categories
        feed_df['google_product_category'] = feed_df['google_product_category_fixed']
        feed_df.drop(columns=['google_product_category_fixed'], inplace=True)

        # Save fixed feed CSV
        feed_df.to_csv(OUTPUT_FIXED_FEED, index=False)

        logger.info(f"✅ Fixed feed saved to: {OUTPUT_FIXED_FEED}")
        logger.info(f"✅ Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
        logger.info(f"ℹ️ Total unmatched invalid categories after fix: {len(unmatched_invalid_categories)}")

    except Exception as e:
        logger.error(f"❌ Error processing feed file: {e}")
        sys.exit(1)

def main():
    taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
    mapping_dict = load_mapping(MAPPING_FILE)
    fix_categories(FEED_FILE, mapping_dict, taxonomy_ids)

if __name__ == "__main__":
    main()
