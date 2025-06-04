import requests

def download_google_taxonomy(save_path='google_product_taxonomy.txt'):
    url = 'https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt'
    response = requests.get(url)
    response.raise_for_status()
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"✅ Google product taxonomy downloaded and saved to {save_path}")

if __name__ == "__main__":
    download_google_taxonomy()
