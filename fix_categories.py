import pandas as pd
import sys
import os

FEED_FILE = 'google_feed/google_merchant_feed.csv'           # Your original feed CSV
MAPPING_FILE = 'category_suggestions.csv'                    # Your invalid-to-valid category map
TAXONOMY_FILE = 'google_product_taxonomy.txt'                # Official taxonomy file
OUTPUT_FIXED_FEED = 'google_merchant_feed_fixed.csv'
OUTPUT_UNMATCHED = 'unmatched_invalid_categories.csv'

def load_taxonomy(taxonomy_file):
    if not os.path.isfile(taxonomy_file):
        print(f"❌ Taxonomy file not found: {taxonomy_file}")
        sys.exit(1)
    try:
        df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
        taxonomy_ids = set(df['category_id'].astype(str).str.strip())
        print(f"✅ Loaded {len(taxonomy_ids)} taxonomy categories from {taxonomy_file}")
        return taxonomy_ids
    except Exception as e:
        print(f"❌ Error loading taxonomy file: {e}")
        sys.exit(1)

def load_mapping(mapping_file):
    if not os.path.isfile(mapping_file):
        print(f"❌ Mapping file not found: {mapping_file}")
        sys.exit(1)
    try:
        df = pd.read_csv(mapping_file, dtype=str)
        required_cols = ['Invalid Category ID', 'Suggested Category ID']
        for col in required_cols:
            if col not in df.columns:
                print(f"❌ Column '{col}' missing in mapping CSV!")
                sys.exit(1)
        mapping_dict = dict(zip(df['Invalid Category ID'].str.strip(), df['Suggested Category ID'].str.strip()))
        print(f"✅ Loaded {len(mapping_dict)} mappings from {mapping_file}")
        return mapping_dict
    except Exception as e:
        print(f"❌ Error loading mapping file: {e}")
        sys.exit(1)

def fix_categories(feed_file, mapping_dict, taxonomy_ids):
    if not os.path.isfile(feed_file):
        print(f"❌ Feed file not found: {feed_file}")
        sys.exit(1)
    try:
        feed_df = pd.read_csv(feed_file, dtype=str)
        if 'google_product_category' not in feed_df.columns:
            print("❌ Column 'google_product_category' not found in feed file!")
            sys.exit(1)

        feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()

        # Apply mapping replacements
        feed_df['google_product_category_fixed'] = feed_df['google_product_category'].apply(
            lambda x: mapping_dict.get(x, x)
        )

        # Find invalid categories after fix
        invalid_after_fix = feed_df[~feed_df['google_product_category_fixed'].isin(taxonomy_ids)]

        # Save unmatched invalid categories for review
        unmatched = invalid_after_fix['google_product_category_fixed'].drop_duplicates().reset_index(drop=True)
        unmatched.to_frame(name='Unmatched Invalid Category').to_csv(OUTPUT_UNMATCHED, index=False)

        # Save fixed feed CSV (replace original category column)
        feed_df['google_product_category'] = feed_df['google_product_category_fixed']
        feed_df.drop(columns=['google_product_category_fixed'], inplace=True)
        feed_df.to_csv(OUTPUT_FIXED_FEED, index=False)

        print(f"✅ Fixed feed saved to: {OUTPUT_FIXED_FEED}")
        print(f"✅ Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
        print(f"ℹ️ Total unmatched invalid categories: {len(unmatched)}")

    except Exception as e:
        print(f"❌ Error processing feed file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
    mapping_dict = load_mapping(MAPPING_FILE)
    fix_categories(FEED_FILE, mapping_dict, taxonomy_ids)
