# Joy&Co Product URL Crawler & Feed Generator

An automated web crawler and product feed generator that scans the Joy&Co website three times a week to collect all product URLs and generate standardized product feeds.

## Overview

This project provides a complete solution for monitoring and exporting product data from the Joy&Co website (https://joyandco.com). The system consists of two main components:

1. **Product URL Crawler** - Recursively scans the Joy&Co website to identify and collect product URLs
2. **Product Feed Generator** - Accesses each product page to extract complete product information and generate standardized feeds in CSV and XML formats

The system runs automatically via GitHub Actions every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4) and commits any new product data to the repository.

## Features

- **Scheduled Crawling**: Automatically runs three times a week (Mon/Wed/Fri) at 1 AM Dubai time
- **Complete Product Discovery**: Recursively crawls all internal pages to discover every product
- **Standardized Feed Generation**: Creates both CSV and XML product feeds in Google Merchant format
- **Data Extraction**: Pulls detailed product information including:
  - Product title
  - Full description
  - Current price
  - Product images
  - Brand information
  - Availability status
- **Version Control**: Maintains a history of all product data over time
- **Manual Trigger Option**: Can be run on-demand through GitHub Actions interface

## Components

### 1. Crawler Script (`crawler.py`)

The primary Python script that performs the website crawling, URL identification, and initial data storage:

- Recursively navigates the Joy&Co website
- Identifies product URLs based on URL path patterns
- Stores discovered URLs in both CSV and XML formats
- Creates timestamped records for tracking

### 2. Feed Generator (`product_feed_generator.py`)

Processes the collected URLs to generate standardized product feeds:

- Visits each product page to extract detailed information
- Extracts full product descriptions and pricing
- Generates Google Merchant-compatible CSV and XML feeds
- Includes comprehensive error handling
- Performs automatic verification of generated files

### 3. GitHub Actions Workflow (`.github/workflows/crawl.yml`)

Configures the automated execution of the entire system:

- Runs every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4)
- Sets up the Python environment
- Executes both the crawler and feed generator scripts
- Commits all generated files to the repository

## Output Files

The system generates four main output files:

1. `product_urls/product_links.csv` - List of all product URLs in CSV format
2. `product_urls/product_links.xml` - List of all product URLs in XML format
3. `google_feed/product_feed.csv` - Complete product feed in CSV format
4. `google_feed/product_feed.xml` - Complete product feed in XML format

## Setup Instructions

1. **Create a GitHub Repository**
   - Create a new repository to host the project

2. **Add Project Files**
   - Add `crawler.py`, `product_feed_generator.py`, and `requirements.txt` to the root directory
   - Create the `.github/workflows/` directory
   - Add `crawl.yml` to the workflows directory

3. **Push to GitHub**
   - Commit and push all files to your repository

4. **Verify GitHub Actions**
   - Navigate to the "Actions" tab in your repository
   - Verify that the workflow is properly configured
   - The system will now run automatically on the scheduled days

## Manual Execution

To run the system manually:

1. Go to your GitHub repository
2. Click on the "Actions" tab at the top
3. Select the "Run Crawler on Mon, Wed, Fri" workflow from the left sidebar
4. Click on the "Run workflow" button (dropdown on the right side)
5. Confirm to run the workflow

## Customization

### Changing the Schedule

To modify when the system runs:

1. Edit the cron expression in `.github/workflows/crawl.yml`
2. The current setting (`0 21 * * 1,3,5`) runs at 21:00 UTC (1:00 AM Dubai time) on Monday, Wednesday, and Friday
3. Refer to [crontab.guru](https://crontab.guru/) for help with cron expressions

### Modifying the Feed Format

To adjust the product feed format:

1. Edit the `generate_csv` and `generate_xml` functions in `product_feed_generator.py`
2. Add or remove fields from the `product_data` dictionary in the `extract_product_data` function

## Requirements

- Python 3.x
- BeautifulSoup4
- Requests
- GitHub account with Actions enabled

## Notes

- This system is designed to be respectful of the target website's resources
- Consider adding delays between requests if crawling a large number of pages
- Always ensure web scraping complies with the target website's terms of service
