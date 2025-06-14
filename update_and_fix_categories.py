name: Run Crawler on Mon, Wed, Fri

on:
  workflow_dispatch:
  schedule:
    - cron: '0 21 * * 1,3,5'  # 1 AM Dubai time on Mon, Wed, Fri

jobs:
  crawl:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      # Calculate SHA256 hash of current feed CSV to detect changes
      - name: Calculate current feed hash
        id: calc_hash
        run: |
          sha256=$(sha256sum google_feed/google_merchant_feed.csv | cut -d' ' -f1)
          echo "current_hash=$sha256" >> $GITHUB_OUTPUT

      # Read last saved feed hash to compare
      - name: Read previous hash
        id: read_prev_hash
        run: |
          if [[ -f .github/last_feed_hash.txt ]]; then
            prev_hash=$(cat .github/last_feed_hash.txt)
          else
            prev_hash=""
          fi
          echo "prev_hash=$prev_hash" >> $GITHUB_OUTPUT

      # Compare current and previous hashes, decide if feed changed
      - name: Compare hashes
        id: check_hash
        run: |
          if [[ "${{ steps.calc_hash.outputs.current_hash }}" != "${{ steps.read_prev_hash.outputs.prev_hash }}" ]]; then
            echo "feed_changed=true" >> $GITHUB_OUTPUT
          else
            echo "feed_changed=false" >> $GITHUB_OUTPUT
          fi

      # Save new hash file if feed changed, commit & push it
      - name: Save new hash
        if: ${{ steps.check_hash.outputs.feed_changed == 'true' }}
        run: |
          echo "${{ steps.calc_hash.outputs.current_hash }}" > .github/last_feed_hash.txt
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .github/last_feed_hash.txt
          git commit -m "Update feed hash [skip ci]"
          git push

      # Cache pip packages to speed up installs
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      # Cache Google product taxonomy file
      - name: Cache Google Product Taxonomy
        id: cache-taxonomy
        uses: actions/cache@v3
        with:
          path: google_product_taxonomy.txt
          key: google-product-taxonomy-${{ runner.os }}-v1
          restore-keys: |
            google-product-taxonomy-${{ runner.os }}-

      # Cache category suggestions mapping file
      - name: Cache category suggestions CSV
        id: cache-category-suggestions
        uses: actions/cache@v3
        with:
          path: category_suggestions.csv
          key: category-suggestions-${{ runner.os }}-v1
          restore-keys: |
            category-suggestions-${{ runner.os }}-

      # Restore cache for seen_products.json (to speed up crawler loading previous data)
      - name: Restore cache for seen_products.json
        id: cache-seen-products
        uses: actions/cache@v3
        with:
          path: seen_products.json
          key: seen-products-${{ runner.os }}-v1
          restore-keys: |
            seen-products-${{ runner.os }}-

      # Set up Python environment
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      # Install required dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Create necessary folders if missing
      - name: Create necessary directories
        run: |
          mkdir -p product_urls google_feed meta_feed

      # Run crawling and feed generation only if feed CSV changed
      - name: Run crawler script
        if: ${{ steps.check_hash.outputs.feed_changed == 'true' }}
        run: python crawler.py

      # After crawling, check if seen_products.json exists for caching
      - name: Check if seen_products.json exists
        id: check_seen_file
        run: |
          if [ -f "seen_products.json" ]; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi

      # DEBUG: List files before caching seen_products.json
      - name: List files before caching seen_products.json
        run: ls -la

      # Cache seen_products.json only if it exists
      - name: Cache seen_products.json
        uses: actions/cache@v3
        if: steps.check_seen_file.outputs.exists == 'true'
        with:
          path: seen_products.json
          key: seen-products-${{ runner.os }}-v1
          restore-keys: |
            seen-products-${{ runner.os }}-

      - name: Run feed generator
        if: ${{ steps.check_hash.outputs.feed_changed == 'true' }}
        run: python product_feed_generator.py

      - name: Run Meta Shopping feed generator
        if: ${{ steps.check_hash.outputs.feed_changed == 'true' }}
        run: python meta_feed_generator.py

      # Download taxonomy only if cache miss
      - name: Download Google product taxonomy
        if: steps.cache-taxonomy.outputs.cache-hit != 'true'
        run: python download_taxonomy.py
        continue-on-error: false

      # Validate categories every run (latest feed)
      - name: Validate Google product categories
        run: python download_and_validate_full.py
        env:
          FEED_FILE: google_feed/google_merchant_feed.csv
        continue-on-error: false

      # Fix invalid categories every run - IMPROVED fix_categories.py integration
      - name: Fix invalid product categories
        run: python fix_categories.py
        env:
          FEED_FILE: google_feed/google_merchant_feed.csv
          MAPPING_FILE: category_suggestions.csv
          TAXONOMY_FILE: google_product_taxonomy.txt

      # Upload fixed feed every run
      - name: Upload fixed feed to Google Sheets
        run: python sheets_publisher.py
        env:
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
          SPREADSHEET_ID: "1aNtP8UJyy8sDYf3tPpCAZt-zMMHwofjpyEqrN9b1bJI"
          WORKSHEET_NAME: "google_merchant_feed"
          FEED_FILE: "google_feed/google_merchant_feed_fixed.csv"

      # Commit and push updated files if any changes
      - name: Commit and push updated files
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"

          for file in product_urls/product_links.csv product_urls/product_links.xml google_feed/product_feed.csv google_feed/product_feed.xml google_feed/google_merchant_feed.csv google_feed/google_merchant_feed_fixed.csv category_validation_full_report.csv unmatched_invalid_categories.csv meta_feed/facebook_product_feed.csv meta_feed/facebook_product_feed.xml; do
            if [ -f "$file" ]; then
              git add "$file"
            fi
          done

          git commit -m "Automated feed update and validation - $(date -u +'%Y-%m-%d %H:%M:%S UTC')" || echo "No changes to commit"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
