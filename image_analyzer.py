import requests
import csv
import os
import sys
import time
import json
from urllib.parse import urljoin, urlparse
from datetime import datetime

# File paths
INPUT_FEED = "google_feed/google_merchant_feed.csv"
OUTPUT_DIR = "image_analysis"
OUTPUT_FILE = f"{OUTPUT_DIR}/image_analysis_results.csv"
ISSUES_FILE = f"{OUTPUT_DIR}/image_processing_issues.csv"
SUMMARY_FILE = f"{OUTPUT_DIR}/image_analysis_summary.md"

# Make sure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configuration
MAX_WORKERS = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def check_image_dimensions(url):
    """Check if an image exists and get basic HTTP information about it"""
    try:
        # Set headers to mimic a browser
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://joyandco.com/",
        }
        
        # Start with a HEAD request to get headers without downloading the full image
        response = requests.head(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Get content type and content length
        content_type = response.headers.get('Content-Type', '')
        content_length = int(response.headers.get('Content-Length', 0))
        
        # Check if it's an image
        is_image = content_type.startswith('image/')
        
        return {
            "url": url,
            "exists": True,
            "content_type": content_type,
            "content_length": content_length,
            "is_image": is_image,
            "file_size_kb": round(content_length / 1024, 2),
            "status_code": response.status_code,
            "result": "success"
        }
    except Exception as e:
        # Return error information if something goes wrong
        return {
            "url": url,
            "exists": False,
            "content_type": "",
            "content_length": 0,
            "is_image": False,
            "file_size_kb": 0,
            "status_code": getattr(e, 'response', {}).get('status_code', 0),
            "result": f"error: {str(e)}"
        }

def load_product_image_urls():
    """Load product IDs and image URLs from the merchant feed"""
    products = []
    
    try:
        with open(INPUT_FEED, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'id' in row and 'image_link' in row:
                    products.append({
                        'id': row['id'],
                        'url': row['image_link'],
                        'title': row.get('title', ''),
                        'brand': row.get('brand', '')
                    })
    except Exception as e:
        print(f"Error loading merchant feed: {e}")
        return []
    
    return products

def analyze_images():
    """Analyze images in the merchant feed"""
    print("Starting image analysis...")
    
    # Load products from merchant feed
    products = load_product_image_urls()
    print(f"Loaded {len(products)} products from merchant feed")
    
    if not products:
        print("No products found. Please check the input file.")
        return []
    
    # Analyze each image
    results = []
    for product in products:
        print(f"Checking: {product['id']} - {product['url']}")
        image_info = check_image_dimensions(product['url'])
        
        # Extract filename from URL
        filename = product['url'].split('/')[-1]
        
        # Extract date from filename if present
        date = ""
        import re
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
        if date_match:
            date = date_match.group(1)
        
        # Create result
        result = {
            "product_id": product['id'],
            "title": product.get('title', ''),
            "brand": product.get('brand', ''),
            "url": product['url'],
            "exists": image_info['exists'],
            "content_type": image_info['content_type'],
            "file_size_kb": image_info['file_size_kb'],
            "status_code": image_info['status_code'],
            "filename": filename,
            "date": date,
            "result": image_info['result']
        }
        
        results.append(result)
        
        # Be polite to the server
        time.sleep(0.5)
    
    return results

def find_potential_issues(results):
    """Identify images that might have issues based on their properties"""
    potential_issues = []
    
    for result in results:
        issues = []
        
        # Skip images that already failed to load
        if "error" in result["result"]:
            issues.append(f"Failed to load image: {result['result']}")
            potential_issues.append({
                "product_id": result["product_id"],
                "issue_title": "Image loading error",
                "details": result["result"]
            })
            continue
        
        # Check if it exists
        if not result["exists"]:
            issues.append("Image does not exist")
            potential_issues.append({
                "product_id": result["product_id"],
                "issue_title": "Image does not exist",
                "details": f"Status code: {result['status_code']}"
            })
            continue
        
        # Check content type
        if not result["content_type"].startswith('image/'):
            issues.append(f"Not an image: {result['content_type']}")
            potential_issues.append({
                "product_id": result["product_id"],
                "issue_title": "Not an image",
                "details": result["content_type"]
            })
            
        # Check file size - too large or too small
        if result["file_size_kb"] > 5120:  # > 5MB
            issues.append(f"File size too large: {result['file_size_kb']} KB (max 5120 KB)")
            potential_issues.append({
                "product_id": result["product_id"],
                "issue_title": "File size too large",
                "details": f"{result['file_size_kb']} KB (max 5120 KB)"
            })
        elif result["file_size_kb"] < 10:  # < 10KB
            issues.append(f"File size too small: {result['file_size_kb']} KB (min 10 KB)")
            potential_issues.append({
                "product_id": result["product_id"],
                "issue_title": "File size too small",
                "details": f"{result['file_size_kb']} KB (min 10 KB)"
            })
            
        # Add any other checks as needed
    
    return potential_issues

def generate_summary_report(results, issues):
    """Generate a markdown summary report"""
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("# Image Analysis Summary\n\n")
        
        # General stats
        success_count = sum(1 for r in results if "error" not in r["result"])
        error_count = len(results) - success_count
        
        f.write(f"**Total Images Analyzed:** {len(results)}\n")
        f.write(f"**Successfully Loaded:** {success_count}\n")
        f.write(f"**Loading Errors:** {error_count}\n")
        f.write(f"**Potential Issues Found:** {len(issues)}\n\n")
        
        # Content type stats
        content_types = {}
        for r in results:
            content_type = r["content_type"]
            if content_type:
                content_types[content_type] = content_types.get(content_type, 0) + 1
        
        f.write("## Content Types\n\n")
        for ct, count in content_types.items():
            f.write(f"* {ct}: {count} images ({(count/len(results)*100):.1f}%)\n")
        
        # Date stats
        dates = {}
        for r in results:
            date = r["date"]
            if date:
                dates[date] = dates.get(date, 0) + 1
        
        f.write("\n## Image Dates\n\n")
        for date, count in sorted(dates.items()):
            f.write(f"* {date}: {count} images ({(count/len(results)*100):.1f}%)\n")
        
        # Most common issues
        if issues:
            issue_types = {}
            for issue in issues:
                issue_type = issue["issue_title"]
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            f.write("\n## Most Common Issues\n\n")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"* {issue_type}: {count} images\n")
            
            f.write("\n## Products with Potential Issues\n\n")
            f.write("| Product ID | Issue |\n")
            f.write("|------------|-------|\n")
            
            for issue in issues[:20]:  # Show top 20 issues
                f.write(f"| {issue['product_id']} | {issue['issue_title']} |\n")
            
            if len(issues) > 20:
                f.write(f"\n*...and {len(issues) - 20} more issues (see CSV file for complete list)*\n")

def main():
    # Analyze images
    results = analyze_images()
    
    # Define CSV columns for results
    fieldnames = [
        "product_id", "title", "brand", "url", "exists", 
        "content_type", "file_size_kb", "status_code", 
        "filename", "date", "result"
    ]
    
    # Write results to CSV
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Find potential issues
    issues = find_potential_issues(results)
    
    # Write issues to CSV
    with open(ISSUES_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["product_id", "issue_title", "details"])
        writer.writeheader()
        for issue in issues:
            writer.writerow(issue)
    
    # Generate summary report
    generate_summary_report(results, issues)
    
    # Print summary
    print(f"\nAnalysis complete. Results saved to {OUTPUT_FILE}")
    print(f"Potential issues saved to {ISSUES_FILE}")
    print(f"Summary report saved to {SUMMARY_FILE}")
    
    # Print stats
    success_count = sum(1 for r in results if "error" not in r["result"])
    error_count = len(results) - success_count
    print(f"Successfully analyzed: {success_count} images")
    print(f"Errors: {error_count} images")
    print(f"Potential issues found: {len(issues)} issues")

if __name__ == "__main__":
    main()
