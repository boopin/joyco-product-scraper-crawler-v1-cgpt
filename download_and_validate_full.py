import requests
import pandas as pd
import os

TAXONOMY_URL = 'https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt'
TAXONOMY_FILE = 'google_product_taxonomy.txt'
FEED_FILE = 'google_feed/google_merchant_feed.csv'  # Update path if needed
OUTPUT_FILE = 'category_validation_full_report.csv'

def download_taxonomy(url, save_path):
    print("Downloading Google product taxonomy...")
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"✅ Taxonomy saved to {save_path}")

def load_taxonomy(tsv_file):
    df = pd.read_csv(tsv_file, sep='\t', header=None, names=['category_id', 'category_name'])
    # Strip spaces in taxonomy IDs
    df['category_id'] = df['category_id'].astype(str).str.strip()
    return set(df['category_id'])

def validate_categories_with_flag(feed_file, taxonomy_ids):
    if feed_file.endswith('.csv'):
        feed_df = pd.read_csv(feed_file, dtype=str)
    else:
        feed_df = pd.read_excel(feed_file, dtype=str)
    
    # Strip spaces in feed category IDs
    feed_df['google_product_category'] = feed_df['google_product_category'].astype(str).str.strip()
    
    feed_df['is_valid_category'] = feed_df['google_product_category'].apply(lambda x: x in taxonomy_ids)
    
    return feed_df

def main():
    download_taxonomy(TAXONOMY_URL, TAXONOMY_FILE)
    taxonomy_ids = load_taxonomy(TAXONOMY_FILE)
    validated_df = validate_categories_with_flag(FEED_FILE, taxonomy_ids)
    
    validated_df.to_csv(OUTPUT_FILE, index=False)
    invalid_count = (~validated_df['is_valid_category']).sum()
    print(f"Total products checked: {len(validated_df)}")
    print(f"Invalid category count: {invalid_count}")
    print(f"Full validation report saved as: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
