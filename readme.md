# Joy&Co Product URL Crawler & Feed Generator with Google Sheets Integration

An automated web crawler and product feed generator that scans the Joy&Co website three times a week to collect all product URLs, generate standardized product feeds, and automatically updates Google Sheets for seamless Google Merchant Center integration.

## Overview

This project provides a complete solution for monitoring and exporting product data from the Joy&Co website (https://joyandco.com). The system consists of three main components:

1. **Product URL Crawler** - Recursively scans the Joy&Co website to identify and collect product URLs
2. **Product Feed Generator** - Accesses each product page to extract complete product information and generate standardized feeds in CSV and XML formats
3. **Google Sheets Publisher** - Automatically updates Google Sheets with fresh product data for Google Merchant Center integration

The system runs automatically via GitHub Actions every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4) and commits any new product data to the repository while simultaneously updating your Google Sheets feed.

## Features

- **Scheduled Crawling**: Automatically runs three times a week (Mon/Wed/Fri) at 1 AM Dubai time
- **Complete Product Discovery**: Recursively crawls all internal pages to discover every product
- **Multi-Platform Feed Generation**: Creates feeds for both Google Merchant Center and Meta Shopping
- **Google Sheets Integration**: Automatically updates your Google Sheets document linked to Google Merchant Center
- **Data Extraction**: Pulls detailed product information including:
  - Product title
  - Full description
  - Current price
  - Product images
  - Brand information
  - Availability status
  - Google product categories
  - MPN (Manufacturer Part Number)
- **Version Control**: Maintains a history of all product data over time
- **Manual Trigger Option**: Can be run on-demand through GitHub Actions interface
- **Error Handling**: Robust error handling with comprehensive logging

## Components

### 1. Crawler Script (`crawler.py`)

The primary Python script that performs the website crawling, URL identification, and initial data storage:

- Recursively navigates the Joy&Co website
- Identifies product URLs based on URL path patterns
- Stores discovered URLs in both CSV and XML formats
- Creates timestamped records for tracking
- Uses bot detection avoidance techniques (user-agent rotation, delays)

### 2. Feed Generator (`product_feed_generator.py`)

Processes the collected URLs to generate standardized product feeds:

- Visits each product page to extract detailed information
- Extracts full product descriptions and pricing
- Generates Google Merchant-compatible CSV and XML feeds
- Includes comprehensive error handling
- Performs automatic verification of generated files

### 3. Meta Feed Generator (`meta_feed_generator.py`)

Creates Meta/Facebook Shopping compatible feeds:

- Converts product data to Meta Shopping format
- Generates both CSV and XML feeds for Facebook catalog
- Ensures compatibility with Facebook advertising platform

### 4. Google Sheets Publisher (`sheets_publisher.py`)

Automatically updates Google Sheets with fresh product data:

- Connects to Google Sheets using service account authentication
- Updates the specified worksheet with latest product feed
- Handles data cleaning (removes NaN values)
- Adds metadata (last updated time, product count)
- Provides comprehensive error handling and logging

### 5. GitHub Actions Workflow (`.github/workflows/crawl.yml`)

Configures the automated execution of the entire system:

- Runs every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4)
- Sets up the Python environment with all required dependencies
- Executes crawler, feed generators, and Google Sheets publisher
- Commits all generated files to the repository
- Includes manual trigger option

## Output Files

The system generates seven main output files:

### Product URLs
1. `product_urls/product_links.csv` - List of all product URLs in CSV format
2. `product_urls/product_links.xml` - List of all product URLs in XML format

### Google Merchant Feeds
3. `google_feed/product_feed.csv` - Complete product feed in CSV format
4. `google_feed/product_feed.xml` - Complete product feed in XML format
5. `google_feed/google_merchant_feed.csv` - Google Merchant Center specific format

### Meta Shopping Feeds
6. `meta_feed/facebook_product_feed.csv` - Meta Shopping feed in CSV format
7. `meta_feed/facebook_product_feed.xml` - Meta Shopping feed in XML format

## Google Sheets Integration Setup

### Prerequisites
- Google Cloud Console account
- Google Sheets document linked to Google Merchant Center
- GitHub repository with Actions enabled

### Step 1: Create Google Service Account

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or select a project**
3. **Enable APIs**:
   - Go to "APIs & Services" → "Library"
   - Enable "Google Sheets API"
   - Enable "Google Drive API"
4. **Create Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: `joy-co-sheets-publisher`
   - Download the JSON key file

### Step 2: Share Google Sheets

1. **Open your Google Sheets document**
2. **Click "Share" button**
3. **Add the service account email** (from the JSON file)
4. **Give "Editor" permissions**
5. **Uncheck "Notify people"**

### Step 3: Add GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add new secret**:
   - Name: `GOOGLE_SHEETS_CREDENTIALS`
   - Value: Entire contents of the downloaded JSON file

### Step 4: Configure Worksheet Name

In `sheets_publisher.py`, update the `WORKSHEET_NAME` variable to match your Google Sheets tab name:

```python
WORKSHEET_NAME = "google_merchant_feed"  # Your tab name
```

## Setup Instructions

### Basic Setup

1. **Create a GitHub Repository**
   - Create a new repository to host the project

2. **Add Project Files**
   - Add all Python scripts to the root directory:
     - `crawler.py`
     - `product_feed_generator.py`
     - `meta_feed_generator.py`
     - `sheets_publisher.py`
     - `requirements.txt`
   - Create the `.github/workflows/` directory
   - Add `crawl.yml` to the workflows directory

3. **Update Requirements**
   - Ensure `requirements.txt` includes:
     ```
     requests==2.31.0
     beautifulsoup4==4.12.2
     gspread>=5.0.0
     google-auth>=2.0.0
     pandas>=1.3.0
     ```

4. **Configure Google Sheets Integration** (follow steps above)

5. **Push to GitHub**
   - Commit and push all files to your repository

6. **Verify GitHub Actions**
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

### Changing Google Sheets Configuration

1. **Different Spreadsheet**: Update `SPREADSHEET_ID` in `sheets_publisher.py`
2. **Different Worksheet**: Update `WORKSHEET_NAME` in `sheets_publisher.py`
3. **Different Data Format**: Modify the CSV generation in `product_feed_generator.py`

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Joy&Co        │    │    GitHub        │    │   Google        │
│   Website       │───▶│    Actions       │───▶│   Sheets        │
│                 │    │                  │    │                 │
│ • Product Pages │    │ • Crawler        │    │ • Live Feed     │
│ • Categories    │    │ • Feed Generator │    │ • Auto Update   │
│ • Inventory     │    │ • Sheets Publisher│   │ • Merchant Sync │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Meta/Facebook  │
                       │   Shopping Feeds │
                       │                  │
                       │ • CSV Format     │
                       │ • XML Format     │
                       │ • Auto Generated │
                       └──────────────────┘
```

## Requirements

- Python 3.x
- BeautifulSoup4
- Requests
- gspread (Google Sheets API)
- google-auth (Authentication)
- pandas (Data processing)
- GitHub account with Actions enabled
- Google Cloud Console account (for service account)

## Data Flow

1. **Crawling**: Discovers all product URLs from Joy&Co website
2. **Extraction**: Visits each product page to extract detailed information
3. **Processing**: Converts data to multiple feed formats (Google Merchant, Meta Shopping)
4. **Publishing**: Updates Google Sheets automatically
5. **Storage**: Commits all data to GitHub for version control

## Monitoring & Logs

The system provides comprehensive logging:

- **Crawler logs**: Track URL discovery and crawling progress
- **Feed generation logs**: Monitor data extraction and file creation
- **Google Sheets logs**: Verify successful uploads and data integrity
- **GitHub Actions logs**: Complete execution history and error tracking

## Troubleshooting

### Common Issues

**Google Sheets Permission Denied**
- Verify service account email is shared with Editor permissions
- Check GOOGLE_SHEETS_CREDENTIALS secret is set correctly

**API Quota Exceeded**
- Google Sheets API has generous limits (100 requests/100 seconds)
- Our batch operations minimize API calls

**Workflow Failures**
- Check GitHub Actions logs for detailed error messages
- Verify all required files are present in repository
- Ensure secrets are properly configured

## Security Features

- **Service Account Authentication**: Minimal required permissions
- **GitHub Secrets**: Encrypted credential storage
- **No Personal Data**: Only product information is processed
- **Audit Trail**: Complete logging of all operations

## Performance

- **Efficient API Usage**: Batch operations minimize Google Sheets API calls
- **Respectful Crawling**: Built-in delays and user-agent rotation
- **Data Validation**: Automatic cleaning and error handling
- **Incremental Updates**: Only processes new or changed data

## Business Benefits

- **Automated Inventory Sync**: Google Shopping ads always use current data
- **Multi-Platform Support**: Simultaneous Google and Meta feed generation
- **Zero Manual Work**: Complete automation with error handling
- **Competitive Advantage**: 3x weekly updates ensure fresh product listings
- **Cost Effective**: Free GitHub Actions execution with enterprise-level reliability

## Notes

- This system is designed to be respectful of the target website's resources
- Includes delays between requests to avoid overwhelming the server
- Always ensure web scraping complies with the target website's terms of service
- Monitor API usage to stay within Google's quotas
- The system handles errors gracefully and continues operation even if individual components fail

---

**🚀 Once configured, your Joy&Co product feeds will automatically sync to Google Merchant Center 3 times per week with zero manual intervention!**
