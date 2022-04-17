# Institute and Author image scraper

This module helps with scraping author and institution images from google.

## Pre-requisites:

1. Pip install Selenium Library
2. Pip install PIL
3. Download Google Chrome
4. Download Google Webdriver based on your Chrome 
version
    > https://chromedriver.chromium.org/downloads

# Setup:
1. > pip install -r requirements.txt
2. Update the chromedriver present in the webdriver/ folder
3. Enter the details of MAG database in db-config.json

# Usage:

1. Scraping Author images which are missing a image_url in MAG database
    > python mt_scrape_author_profiles.py --db_config db-config.json --num_threads=3
2. Fetching and saving institutions logo images:
    > python scrape_inst_logos.py --db_config db-config.json