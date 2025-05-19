import json
import pandas as pd

def main():
    with open("product_feed.json", "r") as f:
        products = json.load(f)

    df = pd.DataFrame(products)

    df.to_csv("product_feed.csv", index=False)
    print("✅ CSV feed saved as product_feed.csv")

if __name__ == "__main__":
    main()
