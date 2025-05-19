import requests
from bs4 import BeautifulSoup
import json
import os

def crawl_product_data(product_urls):
    products = []
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    for url in product_urls:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("h1").get_text(strip=True)
            description_tag = soup.find("meta", {"name": "description"})
            description = description_tag["content"] if description_tag else ""

            price_tag = soup.select_one(".price-item.price-item--regular")
            price = price_tag.get_text(strip=True).replace("AED", "").strip() if price_tag else ""

            image_tag = soup.find("img", {"class": "product__media-img"})
            image_url = image_tag["src"] if image_tag else ""

            product = {
                "id": url.split("/")[-1],
                "title": title,
                "description": description,
                "link": url,
                "image_link": image_url,
                "availability": "in stock",
                "price": price + " AED" if price else "",
                "brand": "Joy and Co",
                "condition": "new"
            }

            products.append(product)

        except Exception as e:
            print(f"Error processing {url}: {e}")

    with open("product_feed.json", "w") as f:
        json.dump(products, f, indent=2)

if __name__ == "__main__":
    product_urls = [
        "https://joyandco.com/product/flower-girl-candleholder-yellow-CA8gpn"
        # Add more product URLs here for testing
    ]
    crawl_product_data(product_urls)
