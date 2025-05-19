import json
import csv

def generate_product_feed():
    with open("product_feed.json", "r") as f:
        products = json.load(f)

    with open("product_feed.csv", "w", newline="") as csvfile:
        fieldnames = [
            "id", "title", "description", "link", "image_link",
            "availability", "price", "brand", "condition"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            writer.writerow(product)

if __name__ == "__main__":
    generate_product_feed()
