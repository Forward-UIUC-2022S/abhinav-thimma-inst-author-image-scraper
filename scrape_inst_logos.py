"""
Time complexity:

size: 25, time: 46.523 s
size: 50, time: 72.11 s
size: 80, time: 146.23 s
"""


from GoogleImageScrapper import GoogleImageScraper
import mysql.connector
import argparse
import json

def scrape_and_update_institution_logos(db, cursor):
    '''
    This function:
    - finds the departments which are missing a logo
    - Scrape Google images for the logo of the department
    - Update the database with the new logo
    '''
    update_cursor = db.cursor()
    image_scrapper = GoogleImageScraper(verbose=False)

    cursor.execute("""
    SELECT Department.id, Institution.name

    FROM Department
    JOIN Institution ON institution_id = Institution.id

    WHERE photo_url IS NULL
    """)

    inst_i = 0
    inst_t = cursor.fetchone()
    scraped_url_map = {}

    while inst_t is not None:

        if inst_i % 20 == 0:
            print("Scraping %sth institution"%(inst_i, ))

        query_str = inst_t[1] + " png"
        image_url = image_scrapper.find_image_urls(query_str)
        scraped_url_map[inst_t[0]] = image_url

        if image_url is not None:

            update_sql = """
            UPDATE Department
            SET photo_url=%s
            WHERE id=%s
            """
            update_params = (image_url, inst_t[0])
            update_cursor.execute(update_sql, update_params)

        else:
            print("No image found for %s, the %sth institution"%(inst_t[1], inst_i))

        inst_t = cursor.fetchone()
        inst_i += 1

        if inst_i % 40 == 0:
            print("Reinitialzing driver")
            image_scrapper.reinitialize_driver()


    db.commit()
    image_scrapper.close_driver()
    return scraped_url_map

def parse_args():
    parser = argparse.ArgumentParser(description="Run baselines.")

    parser.add_argument('--db_config', type=str,
                        help='Path to database config json file.')
    parser.add_argument('--store_results_to_file', type=str, help='Path to store results.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_config_path = args.db_config
    db_config = {}

    with open(db_config_path, 'r') as f:
        db_config = json.load(f)

    db = mysql.connector.connect(
        host=db_config['HOST'],
        port=db_config['PORT'],
        user=db_config['USER'],
        password=db_config['PWD'],
        database=db_config['DB'],
        connect_timeout = 1000,
    )
    cursor = db.cursor(buffered=True)
    print('DB connected')

    scraped_url_map = scrape_and_update_institution_logos(db, cursor)
    
    # storing results to a file
    if(args.store_results_to_file):
        with open(args.store_results_to_file, 'w') as f:
            f.write('DepartmentId, PhotoUrl\n')
            for dept_id, photo_url in scraped_url_map.items():
                f.write(f'{dept_id}, {photo_url}\n')