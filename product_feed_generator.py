import json
import pandas as pd
import os

INPUT_JSON = "product_feed.json"
OUTPUT_CSV = "google_feed/product_feed.csv"
os.makedirs("google_feed", exist_ok=True)

def load_data():
    if not os.path.exists(INPUT_JSON):
        raise FileNotFoundError(f"{INPUT_JSON} not found.")
    with open(INPUT_JSON, "r") as f:
        return json.load(f)

def generate_csv(data):
    df = pd.DataFrame(data)
    
    # Rename fields to match Google Shopping CSV specs
    df = df.rename(columns={
        "title": "title",
        "description": "description",
        "url": "link",
        "image_link": "image_link",
        "brand": "brand",
        "mpn": "mpn",
        "gtin": "gtin",
        "price": "price",
        "availability": "availability",
        "product_type": "product_type",
        "is_new": "is_new"
    })

    # Add static columns for Google Shopping
    df["id"] = df["mpn"]
    df["condition"] = "new"
    df["currency"] = "AED"
    df["price"] = df["price"].apply(lambda x: f"{x} AED" if x else "")
    
    # Reorder columns
    columns = ["id", "title", "description", "link", "image_link", "availability", "price", "brand", "gtin", "mpn", "condition", "product_type", "is_new"]
    df = df[columns]

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Feed saved to: {OUTPUT_CSV}")

def main():
    data = load_data()
    generate_csv(data)

if __name__ == "__main__":
    main()
