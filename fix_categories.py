import csv
import logging
import sys
from rapidfuzz import process, fuzz

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# File paths (adjust as needed)
FEED_FILE = "google_feed/google_merchant_feed.csv"
MAPPING_FILE = "category_suggestions.csv"
TAXONOMY_FILE = "google_product_taxonomy.txt"
FIXED_FEED_FILE = "google_feed/google_merchant_feed_fixed.csv"
UNMATCHED_FILE = "unmatched_invalid_categories.csv"

# Fallback category ID (use sparingly)
FALLBACK_CAT_ID = 6543

# Keyword to Google category ID mapping for quick title-based matching
KEYWORD_CATEGORY_MAP = {
    "vase": 644,            # Home & Garden > Decor > Vases
    "plate": 6208,          # Kitchen & Dining > Tableware > Plates
    "cup": 6231,            # Drinkware > Cups & Mugs
    "mug": 6231,
    "jug": 7492,            # Drinkware > Pitchers & Jugs
    "candle": 5394,         # Lighting > Candles & Holders
    "bowl": 6207,           # Serveware > Bowls
    "tray": 6206,           # Serveware > Trays
    "glass": 6232,          # Drinkware > Glassware
    "photo frame": 5301,    # Decor > Picture Frames
    "napkin": 6301,         # Table Linens > Napkins
    "placemat": 6302,       # Table Linens > Placemats
    "planter": 7381,        # Garden & Outdoor > Planters
    "cake stand": 6410,     # Bakeware & Cake Decorating > Cake Stands
    "teapot": 7311,         # Drinkware > Teapots
    "jar": 5302             # Kitchen & Dining > Storage Jars & Containers
}

def load_taxonomy(filepath):
    taxonomy = {}
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.split(' - ', 1)
            if len(parts) != 2:
                continue
            cat_id_str, cat_name = parts
            try:
                cat_id = int(cat_id_str.strip())
                taxonomy[cat_id] = cat_name.strip().lower()
            except ValueError:
                continue
    logger.info(f"✅ Loaded {len(taxonomy)} taxonomy categories from {filepath}")
    return taxonomy

def load_mappings(filepath):
    mapping = {}
    with open(filepath, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            invalid = row.get("invalid_category_id", "").strip()
            valid_id = row.get("valid_category_id", "").strip()
            if not invalid or not valid_id:
                logger.warning(f"Skipping incomplete row: {row}")
                continue
            try:
                valid_id_int = int(valid_id)
                mapping[invalid] = valid_id_int
                count += 1
            except ValueError:
                logger.warning(f"Invalid valid_category_id in mapping CSV: {valid_id}")
    logger.info(f"✅ Loaded {count} category mappings from {filepath}")
    return mapping

def fuzzy_match_category_name(invalid_cat, taxonomy_names):
    invalid_cat_norm = invalid_cat.lower().strip()
    match, score, idx = process.extractOne(
        invalid_cat_norm,
        taxonomy_names,
        scorer=fuzz.token_sort_ratio
    )
    logger.debug(f"Fuzzy match for '{invalid_cat}' -> '{match}' with score {score}")
    return match, score, idx

def keyword_category_match(product_title):
    title_lower = product_title.lower()
    for keyword, cat_id in KEYWORD_CATEGORY_MAP.items():
        if keyword in title_lower:
            return cat_id
    return None

def fix_categories():
    taxonomy = load_taxonomy(TAXONOMY_FILE)
    mapping = load_mappings(MAPPING_FILE)

    taxonomy_names = list(taxonomy.values())
    taxonomy_ids = list(taxonomy.keys())

    unmatched_categories = set()
    total_products = 0
    fixed_count = 0

    with open(FEED_FILE, encoding='utf-8', newline='') as infile, \
         open(FIXED_FEED_FILE, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if "google_product_category" not in fieldnames:
            logger.error("Feed file missing 'google_product_category' column.")
            return

        # Replace 'title' below with your actual product title column name if different
        if "title" not in fieldnames:
            logger.warning("Feed file missing 'title' column; keyword matching on title will be skipped.")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total_products += 1
            orig_cat = row["google_product_category"].strip()
            product_title = row.get("title", "")

            # Step 1: Exact mapping from CSV
            if orig_cat in mapping:
                new_cat_id = mapping[orig_cat]
                row["google_product_category"] = str(new_cat_id)
                fixed_count += 1
                logger.info(f"Exact mapping: '{orig_cat}' -> '{new_cat_id}'")

            else:
                # Step 1b: Try keyword matching on product title if available
                if product_title:
                    matched_cat = keyword_category_match(product_title)
                    if matched_cat:
                        row["google_product_category"] = str(matched_cat)
                        fixed_count += 1
                        logger.info(f"Keyword matched category: '{product_title}' -> '{matched_cat}'")
                        writer.writerow(row)
                        continue  # proceed to next product row

                # Step 2: Try interpret as int category ID, check taxonomy
                try:
                    orig_cat_int = int(orig_cat)
                    if orig_cat_int in taxonomy:
                        # Valid category, no change needed
                        pass
                    else:
                        # Step 3: Fuzzy match on category names
                        match, score, idx = fuzzy_match_category_name(orig_cat, taxonomy_names)
                        if score >= 70:
                            matched_id = taxonomy_ids[idx]
                            row["google_product_category"] = str(matched_id)
                            fixed_count += 1
                            logger.info(f"Fuzzy matched ID: '{orig_cat}' -> '{matched_id}' (score {score})")
                        else:
                            unmatched_categories.add(orig_cat)
                            row["google_product_category"] = str(FALLBACK_CAT_ID)
                            logger.warning(f"No good fuzzy match for '{orig_cat}'. Assigned fallback category {FALLBACK_CAT_ID}.")
                except ValueError:
                    # Non-numeric invalid category - fuzzy match by name directly
                    match, score, idx = fuzzy_match_category_name(orig_cat, taxonomy_names)
                    if score >= 70:
                        matched_id = taxonomy_ids[idx]
                        row["google_product_category"] = str(matched_id)
                        fixed_count += 1
                        logger.info(f"Fuzzy matched name: '{orig_cat}' -> '{matched_id}' (score {score})")
                    else:
                        unmatched_categories.add(orig_cat)
                        row["google_product_category"] = str(FALLBACK_CAT_ID)
                        logger.warning(f"No good fuzzy match for '{orig_cat}'. Assigned fallback category {FALLBACK_CAT_ID}.")

            writer.writerow(row)

    logger.info(f"✅ Fixed categories for {fixed_count} out of {total_products} products.")
    logger.info(f"⚠️ Total unmatched invalid categories after fix: {len(unmatched_categories)}")

    # Save unmatched categories for manual review
    with open(UNMATCHED_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["unmatched_invalid_category"])
        for cat in sorted(unmatched_categories):
            writer.writerow([cat])
    logger.info(f"⚠️ Unmatched invalid categories saved to: {UNMATCHED_FILE}")

if __name__ == "__main__":
    fix_categories()
