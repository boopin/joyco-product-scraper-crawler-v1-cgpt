# Joy&Co Product URL Crawler & Feed Generator with Google Sheets Integration

An automated web crawler and product feed generator that scans the Joy&Co website three times a week to collect all product URLs, generate standardized product feeds, and automatically updates Google Sheets for seamless Google Merchant Center and Meta Shopping integration.

## Overview

This project provides a complete solution for monitoring and exporting product data from the Joy&Co website (https://joyandco.com). The system consists of four main components:

1. **Product URL Crawler** - Recursively scans the Joy&Co website to identify and collect product URLs
2. **Product Feed Generator** - Accesses each product page to extract complete product information and generate standardized feeds in CSV and XML formats
3. **Meta Feed Generator** - Creates Meta/Facebook Shopping compatible feeds
4. **Google Sheets Publisher** - Automatically updates Google Sheets with fresh product data for both Google Merchant Center and Meta Shopping integration

The system runs automatically via GitHub Actions every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4) and commits any new product data to the repository while simultaneously updating your Google Sheets feeds.

## Features

- **Scheduled Crawling**: Automatically runs three times a week (Mon/Wed/Fri) at 1 AM Dubai time
- **Complete Product Discovery**: Recursively crawls all internal pages to discover every product
- **Multi-Platform Feed Generation**: Creates feeds for both Google Merchant Center and Meta Shopping
- **Dual Google Sheets Integration**: Automatically updates separate Google Sheets for Google and Meta feeds
- **Categorization Reports**: Generates detailed reports on product categorization and updates
- **Enhanced Change Detection**: Only updates sheets when actual changes are detected
- **Data Extraction**: Pulls detailed product information including:
  - Product title
  - Full description
  - Current price
  - Product images
  - Brand information
  - Availability status
  - Google product categories
  - Facebook/Meta product categories
  - MPN (Manufacturer Part Number)
- **Version Control**: Maintains a history of all product data over time
- **Manual Trigger Option**: Can be run on-demand through GitHub Actions interface
- **Error Handling**: Robust error handling with comprehensive logging
- **Report Archives**: Timestamped categorization reports for historical tracking

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
- Maps Google categories to Facebook categories
- Generates both CSV and XML feeds for Facebook catalog
- Ensures compatibility with Facebook advertising platform
- Includes Facebook-specific fields and formatting

### 4. Google Sheets Publisher (`sheets_publisher.py`)

Automatically updates Google Sheets with fresh product data:

- Connects to Google Sheets using service account authentication
- Updates specified worksheets with latest product feeds
- Handles data cleaning (removes NaN values)
- Adds metadata (last updated time, product count)
- Provides comprehensive error handling and logging
- Supports multiple spreadsheet targets

### 5. Category Updater (`category_updater.py`)

Enhances product categorization and generates reports:

- Auto-assigns Google product categories
- Generates detailed categorization review reports
- Tracks categorization changes and improvements
- Creates timestamped reports for audit trails

### 6. GitHub Actions Workflow (`.github/workflows/crawl.yml`)

Configures the automated execution of the entire system:

- Runs every Monday, Wednesday, and Friday at 1 AM Dubai time (UTC+4)
- Sets up the Python environment with all required dependencies
- Executes crawler, feed generators, and Google Sheets publisher
- Commits all generated files and reports to the repository
- Includes manual trigger option
- Handles both Google and Meta feed publishing independently

## Output Files

The system generates multiple output files organized in directories:

### Product URLs
1. `product_urls/product_links.csv` - List of all product URLs in CSV format
2. `product_urls/product_links.xml` - List of all product URLs in XML format

### Google Merchant Feeds
3. `google_feed/product_feed.csv` - Complete product feed in CSV format
4. `google_feed/product_feed.xml` - Complete product feed in XML format
5. `google_feed/google_merchant_feed.csv` - Google Merchant Center specific format
6. `google_feed/google_merchant_feed_updated.csv` - Enhanced version with categories

### Meta Shopping Feeds
7. `meta_feed/facebook_product_feed.csv` - Meta Shopping feed in CSV format
8. `meta_feed/facebook_product_feed.xml` - Meta Shopping feed in XML format

### Categorization Reports
9. `reports/categorization_review_report_latest.csv` - Latest categorization report
10. `reports/categorization_review_report_YYYY-MM-DD_HH-MM.csv` - Timestamped reports

## Google Sheets Integration Setup

### Prerequisites
- Google Cloud Console account
- Two Google Sheets documents (one for Google Merchant, one for Meta Shopping)
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

**For Google Merchant Feed:**
1. **Open your Google Merchant Center linked spreadsheet**
2. **Click "Share" button**
3. **Add the service account email** (from the JSON file)
4. **Give "Editor" permissions**
5. **Uncheck "Notify people"**

**For Meta Shopping Feed:**
1. **Open your Meta Shopping spreadsheet**
2. **Follow the same sharing process**
3. **Ensure the worksheet is named "facebook_product_feed"**

### Step 3: Add GitHub Secrets

1. **Go to your GitHub repository**
2. **Navigate to Settings → Secrets and variables → Actions**
3. **Add new secret**:
   - Name: `GOOGLE_SHEETS_CREDENTIALS`
   - Value: Entire contents of the downloaded JSON file

### Step 4: Configure Spreadsheet IDs

In `.github/workflows/crawl.yml`, the spreadsheet IDs are configured:

**Google Merchant Feed:**
```yaml
SPREADSHEET_ID: "1aNtP8UJyy8sDYf3tPpCAZt-zMMHwofjpyEqrN9b1bJI"
WORKSHEET_NAME: "google_merchant_feed"
```

**Meta Shopping Feed:**
```yaml
SPREADSHEET_ID: "16o2rq9n5E_oIoqb0wzyDWOo3HbvVg2Gnu94KnltuP1Y"
WORKSHEET_NAME: "facebook_product_feed"
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
     - `category_updater.py`
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

**For Google Merchant Feed:**
1. **Different Spreadsheet**: Update `SPREADSHEET_ID` in the Google feed publishing step
2. **Different Worksheet**: Update `WORKSHEET_NAME` in the workflow

**For Meta Shopping Feed:**
1. **Different Spreadsheet**: Update `SPREADSHEET_ID` in the Meta feed publishing step
2. **Different Worksheet**: Update `WORKSHEET_NAME` in the workflow

### Adding New Feed Platforms

To add support for additional platforms (Amazon, eBay, etc.):

1. Create a new feed generator script (e.g., `amazon_feed_generator.py`)
2. Add the generator to the workflow
3. Configure additional Google Sheets integration if needed

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Joy&Co        │    │    GitHub        │    │   Google        │
│   Website       │───▶│    Actions       │───▶│   Sheets        │
│                 │    │                  │    │                 │
│ • Product Pages │    │ • Crawler        │    │ • Google Feed   │
│ • Categories    │    │ • Feed Generators│    │ • Meta Feed     │
│ • Inventory     │    │ • Sheets Publisher│   │ • Auto Update   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Categorization │    │   Google        │
                       │   Reports        │    │   Merchant      │
                       │                  │    │   Center        │
                       │ • Timestamped    │    │                 │
                       │ • Audit Trail    │    │ • Live Sync     │
                       │ • GitHub Archive │    │ • Ad Integration│
                       └──────────────────┘    └─────────────────┘
```

## Enhanced Workflow Features

### Change Detection System

The system now includes sophisticated change detection:

- **Hash-based comparison**: Only updates when feed content actually changes
- **Independent tracking**: Google and Meta feeds are tracked separately
- **Efficient processing**: Skips unnecessary API calls when no changes exist
- **Detailed logging**: Shows exactly what changed and when

### Report Generation

**Categorization Reports Include:**
- Products with category assignments
- Category mapping accuracy
- Failed categorizations
- Timestamp and change tracking
- Historical comparison data

**Report Locations:**
- `reports/categorization_review_report_latest.csv` - Always current
- `reports/categorization_review_report_YYYY-MM-DD_HH-MM.csv` - Historical archives
- GitHub Actions artifacts - Downloadable for 30 days

### Error Handling & Recovery

- **Graceful degradation**: System continues even if individual components fail
- **Retry mechanisms**: Automatic retry for temporary failures
- **Comprehensive logging**: Detailed error tracking and debugging information
- **State preservation**: Maintains progress even across failed runs

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
4. **Categorization**: Auto-assigns categories and generates reports
5. **Change Detection**: Compares new data with previous versions
6. **Publishing**: Updates Google Sheets automatically (only when changed)
7. **Storage**: Commits all data and reports to GitHub for version control
8. **Archiving**: Creates downloadable artifacts and timestamped reports

## Monitoring & Logs

The system provides comprehensive logging:

- **Crawler logs**: Track URL discovery and crawling progress
- **Feed generation logs**: Monitor data extraction and file creation
- **Categorization logs**: Track category assignments and improvements
- **Change detection logs**: Show what data changed between runs
- **Google Sheets logs**: Verify successful uploads and data integrity
- **GitHub Actions logs**: Complete execution history and error tracking

### Key Log Messages to Watch:

**Successful Operations:**
- `✅ Google feed changes detected - will publish to Google Sheets`
- `✅ Meta feed changes detected - will publish to Google Sheets`
- `📊 Categorization report found - preparing for commit`

**No Changes (Normal):**
- `ℹ️ No Google feed changes detected - skipping Google publish`
- `ℹ️ No Meta feed changes detected - skipping Meta publish`

## Troubleshooting

### Common Issues

**Google Sheets Permission Denied**
- Verify service account email is shared with Editor permissions on both sheets
- Check GOOGLE_SHEETS_CREDENTIALS secret is set correctly
- Ensure both spreadsheet IDs are correct in the workflow

**Workflow Only Updates One Feed**
- This is normal behavior - feeds update independently based on changes
- Check change detection logs to see which feeds have modifications

**Missing Reports Folder**
- Reports are only created when categorization work is performed
- Check "Prepare categorization report for commit" step in logs
- Empty categorization runs won't generate reports

**API Quota Exceeded**
- Google Sheets API has generous limits (100 requests/100 seconds)
- Our batch operations minimize API calls
- Consider adding delays if hitting limits

**Hash File Errors**
- Hash files track changes between runs
- Delete `.github/last_*_hash.txt` files to force full update
- System will recreate hash files automatically

## Security Features

- **Service Account Authentication**: Minimal required permissions
- **GitHub Secrets**: Encrypted credential storage
- **No Personal Data**: Only product information is processed
- **Audit Trail**: Complete logging of all operations
- **Change Tracking**: Hash-based verification of data integrity

## Performance Optimizations

- **Efficient API Usage**: Batch operations minimize Google Sheets API calls
- **Change Detection**: Only processes and uploads when data actually changes
- **Respectful Crawling**: Built-in delays and user-agent rotation
- **Data Validation**: Automatic cleaning and error handling
- **Incremental Updates**: Preserves existing data when no changes detected
- **Parallel Processing**: Independent handling of Google and Meta feeds

## Business Benefits

- **Automated Multi-Platform Sync**: Both Google Shopping and Meta ads use current data
- **Independent Feed Management**: Google and Meta feeds update independently
- **Zero Manual Work**: Complete automation with intelligent change detection
- **Competitive Advantage**: 3x weekly updates ensure fresh product listings
- **Cost Effective**: Free GitHub Actions execution with enterprise-level reliability
- **Audit Compliance**: Complete categorization and change tracking
- **Data Integrity**: Hash-based verification ensures accuracy

## Advanced Features

### Smart Change Detection
- **Hash Comparison**: Uses SHA256 hashes to detect actual content changes
- **Independent Tracking**: Separate change detection for each feed type
- **Selective Updates**: Only updates changed feeds, saving API quota and processing time

### Report Management
- **Automatic Archiving**: Creates timestamped report copies
- **Latest Version Tracking**: Always maintains current report as "latest"
- **GitHub Integration**: Reports committed to repository for version control
- **Download Options**: Reports available as GitHub Actions artifacts

### Multi-Platform Support
- **Google Merchant Center**: Optimized for Google Shopping campaigns
- **Meta Shopping**: Facebook and Instagram shopping integration
- **Extensible Architecture**: Easy to add new platforms (Amazon, eBay, etc.)

## Notes

- This system is designed to be respectful of the target website's resources
- Includes delays between requests to avoid overwhelming the server
- Always ensure web scraping complies with the target website's terms of service
- Monitor API usage to stay within Google's quotas
- The system handles errors gracefully and continues operation even if individual components fail
- Change detection prevents unnecessary API calls and maintains efficiency
- Reports provide valuable insights into product categorization and data quality

## Version History

- **v1.0**: Basic crawler and Google Sheets integration
- **v2.0**: Added Meta Shopping feed support
- **v3.0**: Enhanced categorization and reporting
- **v4.0**: Smart change detection and dual Google Sheets publishing (current)

---

**🚀 Once configured, your Joy&Co product feeds will automatically sync to both Google Merchant Center and Meta Shopping platforms 3 times per week with intelligent change detection and zero manual intervention!**
