import pandas as pd

FEED_FILE = 'google_merchant_feed.csv'           # Your original feed CSV
MAPPING_FILE = 'category_suggestions.csv'        # Your invalid-to-valid category map
TAXONOMY_FILE = 'google_product_taxonomy.txt'    # Official taxonomy file
OUTPUT_FIXED_FEED = 'google_merchant_feed_fixed.csv'
OUTPUT_UNMATCHED = 'unmatched_invalid_categories.csv'

def load_taxonomy(taxonomy_file):
    df = pd.read_csv(taxonomy_file, sep='\t', header=None, names=['category_id', 'category_name'])
    return set(df['category_id'].astype(str).str.strip())

def load_mapping(mapping_file):
    df = pd.read_csv(mapping_file, dtype=str)
    mapping_dict = dict(zip(df['Invalid Category ID'].str.strip(), df['Suggested Category ID'].str.strip()))
    return mapping_dict

def fix_categories(feed_file, mapping_dict, taxonomy_ids):
    feed_df = pd.read_csv(feed_file, dtype=str)
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

    print(f"Fixed feed saved to: {OUTPUT_FIXED_FEED}")
    print(f"Unmatched invalid categories saved to: {OUTPUT_UNMATCHED}")
    print(f"Total unmatched invalid categories: {len(unmatched)}")

if __name__ == "__main__":
    taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
    mapping_dict = load_mapping(MAPPING_FILE)
    fix_categories(FEED_FILE, mapping_dict, taxonomy_ids)
