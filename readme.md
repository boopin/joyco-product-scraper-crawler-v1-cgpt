# Joy&Co Product URL Crawler

An automated web crawler that scans the Joy&Co website daily to collect and track all product URLs.

## Overview

This project provides a Python-based web crawler that automatically scans the Joy&Co website (https://joyandco.com) on a daily schedule to identify and collect all product URLs. The crawler recursively navigates through the website, identifying product pages, and saves the collected URLs to both CSV and XML formats.

The system is designed to run autonomously via GitHub Actions, executing at 1 AM Dubai time (UTC+4) each day, and automatically committing any newly discovered product URLs to the repository.

## Features

- Automated daily crawling of the Joy&Co website
- Identification of product URLs based on URL path patterns
- Recursive crawling to discover all internal pages
- Error handling for failed requests
- Storage of product URLs in both CSV and XML formats
- Timestamp tracking for URL discovery
- Automated execution via GitHub Actions
- Version control of product URL database

## Components

### Main Crawler Script (`crawler.py`)

The primary Python script that performs the website crawling, URL identification, and data storage. It utilizes BeautifulSoup for HTML parsing and includes:

- Recursive crawling functionality
- URL validation and filtering
- Product URL identification
- Error handling
- CSV and XML export options

### Requirements File (`requirements.txt`)

Lists the Python dependencies required:
- requests==2.31.0
- beautifulsoup4==4.12.2

### GitHub Actions Workflow (`.github/workflows/crawl.yml`)

Configures the automated execution of the crawler:
- Runs daily at 1 AM Dubai time
- Sets up the Python environment
- Executes the crawler script
- Commits and pushes any new URLs to the repository

## Setup Instructions

1. **Create a GitHub Repository**
   - Create a new repository on GitHub to host the project

2. **Add Project Files**
   - Add `crawler.py` and `requirements.txt` to the root directory
   - Create the `.github/workflows/` directory
   - Add `crawl.yml` to the workflows directory

3. **Push to GitHub**
   - Commit and push all files to your repository

4. **Verify GitHub Actions**
   - Navigate to the "Actions" tab in your repository
   - Verify that the workflow is properly configured
   - The crawler will now run automatically at the scheduled time

## Customization

### Changing the Target Website

To modify the crawler for a different website:
1. Update the `BASE_URL` constant in `crawler.py`
2. Adjust the product URL identification logic (currently `/product/`)
3. Test the crawler to ensure it works with the new website structure

### Modifying the Schedule

To change when the crawler runs:
1. Edit the cron expression in `.github/workflows/crawl.yml`
2. The current setting (`0 21 * * *`) runs at 21:00 UTC (1:00 AM Dubai time)

## Example Output

### CSV Format (`product_links.csv`)
```
url,timestamp
https://joyandco.com/product/sample-product-1,2025-05-17T10:30:45.123456
https://joyandco.com/product/sample-product-2,2025-05-17T10:30:45.234567
```

### XML Format (`product_links.xml`)
```xml
<products>
  <product>
    <url>https://joyandco.com/product/sample-product-1</url>
    <timestamp>2025-05-17T10:30:45.123456</timestamp>
  </product>
  <product>
    <url>https://joyandco.com/product/sample-product-2</url>
    <timestamp>2025-05-17T10:30:45.234567</timestamp>
  </product>
</products>
```

## Notes

- This crawler is designed to be respectful of the target website's resources
- No rate limiting is currently implemented; consider adding delays between requests if needed
- Always ensure web scraping complies with the target website's terms of service
- The system is configured for minimal maintenance, with automated execution and version control

