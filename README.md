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

## Through terminal:
1. Scraping Author images which are missing a image_url in MAG database
    > python mt_scrape_author_profiles.py --db_config db-config.json --num_threads=3 --store_results_to_file ./author_results.csv
2. Fetching and saving institutions logo images:
    > python scrape_inst_logos.py --db_config db-config.json --store_results_to_file ./inst_logo_results.csv

## Importing specific functions/ classes:
1. Scraping Author images which are missing a image_url in MAG database

    ```
    # importing and initializing the scraper

    from mt_scrape_author_profiles import AuthorProfileImageScraper 
    author_image_scraper = AuthorProfileImageScraper()
    ```

    - update_authors_with_missing_photo(cursor):
      This method can be used to update a list at class level which contains AuthorIds which are missing a photo_url
        ```
        # finding authors with missing images and fetching the list

        author_image_scraper.update_authors_with_missing_photo(cursor)
        author_image_scraper.get_author_ts()
        ```
    
    - thread_search, args=(task_lock, write_lock, pbar)): This method can be used to search for author profile images and depends on the class level list "author_ts" for AuthorId's

        ```
        # initilizing the thread_search parameters

        task_lock = threading.Lock()
        write_lock = threading.Lock()
        pbar = tqdm(total=len(author_image_scraper.get_author_ts()))
        ```

        ```
        # using the thread_search and fetching the author_id_to_url map

        author_image_scraper.thread_search, args=(task_lock, write_lock, pbar))
        author_image_scraper.get_author_id_to_url()
        ```

2. Fetching institutions logo images:
    ```
    # importing the function

    from scrape_inst_logos import scrape_and_update_institution_logos
    ```

    The method takes db and cursor generated from mysql.connector. Please find a sample for initialization below:
    ```
    db = mysql.connector.connect(
        host=db_config['HOST'],
        port=db_config['PORT'],
        user=db_config['USER'],
        password=db_config['PWD'],
        database=db_config['DB'],
        connect_timeout = 1000,
    )
    cursor = db.cursor(buffered=True)
    ```
    
    ```
    # using the function to fetch a map of form {'<DepartmentID>': '<Inst_Logo_URL>'}
    # NOTE: This function updates the urls in DB as well

    scraped_url_map = scrape_and_update_institution_logos(db, cursor)
    ```
