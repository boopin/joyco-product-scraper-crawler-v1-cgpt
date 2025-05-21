import requests
from PIL import Image
from io import BytesIO
import csv
import time
from concurrent.futures import ThreadPoolExecutor

# List of image URLs to analyze
# You can modify this list or load from a file
IMAGE_URLS = [
    # Problematic images
    ("azure-tower-vase-usiPgp", "https://joyandco.com/storage/app/public/product/2025-05-11-68206bfe624fb.webp", "issue"),
    ("bold-stripes-vase-IErdVl", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf70ede34b1.webp", "issue"),
    ("bubble-bliss-small-green-vase-fELe5t", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf7306134f3.webp", "issue"),
    ("cherry-blossom-lidded-vase-lKXu7G", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf8ba748b21.webp", "issue"),
    ("classic-yellow-porcelain-vase-m-oMwtLG", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf400f60770.webp", "issue"),
    ("disks-vase-lLL4HA", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf459de769a.webp", "issue"),
    ("sugar-bowl-KoIAB8", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf585e72c4b.webp", "issue"),
    ("sunshine-glass-vase-Gqvfu5", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf606f10cd6.webp", "issue"),
    ("tangerine-twist-vase-m7G1iP", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf6e3cef58c.webp", "issue"),
    ("whimsy-jar-PPY9tL", "https://joyandco.com/storage/app/public/product/2025-03-20-67dbb78be8e8b.webp", "issue"),
    
    # Add some working images for comparison
    ("abracadabra-coffee-cups-set-xUdyr3", "https://joyandco.com/storage/app/public/product/2025-03-03-67c6307a9c180.webp", "success"),
    ("abracadabra-destino-dinner-plate-ZwL71a", "https://joyandco.com/storage/app/public/product/2025-02-19-67b5a826f01ca.webp", "success"),
    ("aurora-vase-QtwQO7", "https://joyandco.com/storage/app/public/product/2025-02-26-67bf6f23a92af.webp", "success"),
    ("skyline-vase-9yZABA", "https://joyandco.com/storage/app/public/product/2025-05-11-68206c822381c.webp", "success"),
    ("sugarline-vase-9rFoY2", "https://joyandco.com/storage/app/public/product/2025-05-11-68206aee2d7ac.webp", "success")
]

OUTPUT_FILE = "image_analysis.csv"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def analyze_image(product_id, url, status):
    """Analyze a single image and return its properties"""
    try:
        # Print progress
        print(f"Processing: {url}")
        
        # Set headers to mimic a browser
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://joyandco.com/",
        }
        
        # Download the image
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Get file size
        file_size_kb = len(response.content) / 1024
        
        # Load the image
        img = Image.open(BytesIO(response.content))
        
        # Extract information
        width, height = img.size
        aspect_ratio = width / height if height > 0 else 0
        format_type = img.format
        mode = img.mode
        
        # Extract filename from URL
        filename = url.split('/')[-1]
        
        # Get data about transparency
        has_transparency = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
        
        # Get more detailed format info if available
        format_details = getattr(img, 'format_description', '') or ''
        
        return {
            "product_id": product_id,
            "url": url,
            "status": status,
            "width": width,
            "height": height,
            "aspect_ratio": round(aspect_ratio, 2),
            "file_size_kb": round(file_size_kb, 2),
            "format": format_type,
            "color_mode": mode,
            "has_transparency": has_transparency,
            "format_details": format_details,
            "filename": filename,
            "result": "success"
        }
    except Exception as e:
        # Return error information if something goes wrong
        return {
            "product_id": product_id,
            "url": url,
            "status": status,
            "width": 0,
            "height": 0,
            "aspect_ratio": 0,
            "file_size_kb": 0,
            "format": "",
            "color_mode": "",
            "has_transparency": "",
            "format_details": "",
            "filename": url.split('/')[-1],
            "result": f"error: {str(e)}"
        }

def main():
    # Define CSV columns
    fieldnames = [
        "product_id", "status", "result", "width", "height", "aspect_ratio", 
        "file_size_kb", "format", "color_mode", "has_transparency", 
        "format_details", "filename", "url"
    ]
    
    # Analyze images in parallel
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(analyze_image, product_id, url, status) 
                  for product_id, url, status in IMAGE_URLS]
        
        for future in futures:
            results.append(future.result())
    
    # Write results to CSV
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\nAnalysis complete. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    success_count = sum(1 for r in results if r["result"] == "success")
    error_count = len(results) - success_count
    print(f"Successfully analyzed: {success_count} images")
    print(f"Errors: {error_count} images")
    
    # Print stats on issues vs success
    issue_images = [r for r in results if r["status"] == "issue" and r["result"] == "success"]
    success_images = [r for r in results if r["status"] == "success" and r["result"] == "success"]
    
    if issue_images and success_images:
        print("\nComparison of Issue vs Success Images:")
        
        avg_width_issue = sum(img["width"] for img in issue_images) / len(issue_images)
        avg_height_issue = sum(img["height"] for img in issue_images) / len(issue_images)
        avg_size_issue = sum(img["file_size_kb"] for img in issue_images) / len(issue_images)
        
        avg_width_success = sum(img["width"] for img in success_images) / len(success_images)
        avg_height_success = sum(img["height"] for img in success_images) / len(success_images)
        avg_size_success = sum(img["file_size_kb"] for img in success_images) / len(success_images)
        
        print(f"Issue Images (Avg): {avg_width_issue:.0f}x{avg_height_issue:.0f} px, {avg_size_issue:.2f} KB")
        print(f"Success Images (Avg): {avg_width_success:.0f}x{avg_height_success:.0f} px, {avg_size_success:.2f} KB")

if __name__ == "__main__":
    main()
