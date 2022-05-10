"""
Thread performance (100 authors):
num_threads: 20, time: 87 s
num_threads: 15, time: 85 s
num_threads: 10, time: 73 s
num_threads: 7, time: 96 s
num_threads: 6, time: 60.7 s
num_threads: 5, time: 64 s
num_threads: 4, time: 67 s
num_threads: 3, time: 62 s
num_threads: 2, time: 79 s


Time experiments (6 threads):

size: 100, time: 61 s
size: 250, time: 180 s
size: 350, time: 240 s
size: 16324, time: ~3 hr 30 mins
"""
import threading
import mysql.connector
import html
from GoogleImageScrapper import GoogleImageScraper
import argparse
from tqdm import tqdm
import json

class AuthorProfileImageScraper:
    def __init__(self) -> None:
        pass
        self.author_ts = [] # This variable is used a shared queue between multiple threads
        self.author_id_to_url = {}
    
    def get_author_ts(self):
        return self.author_ts
    
    def get_author_id_to_url(self):
        return self.author_id_to_url

    def update_authors_with_missing_photo(self, cursor):
        cursor.execute("""
        SELECT Author.id, Author.name, Institution.name
        FROM Author
        JOIN Department  ON department_id = Department.id
        JOIN Institution ON institution_id = Institution.id
        WHERE Author.photo_url IS NULL
        """)

        self.author_ts = cursor.fetchall()


    def thread_search(self, task_lock, write_lock, pbar):
        '''
        This function is run on multiple threads.
        - It takes a task from the queue (in a synchronized way)
        - It searches for the image of the author
        - It updates the database with the image url
        '''
        pid = threading.get_ident()
        image_scrapper = GoogleImageScraper(verbose=False)
        num_local_scraped = 0
        print("Initialzed thread {}".format(pid))

        while True:

            # Critical section, checking remaining authors
            task_lock.acquire()
            curr_author_t = None
            if len(self.author_ts) > 0:
                curr_author_t = self.author_ts.pop()
            task_lock.release()

            if curr_author_t is None:
                break
            else:
                curr_author_id = curr_author_t[0]
                query_str = curr_author_t[1] + " " + curr_author_t[2]
                query_str = html.unescape(query_str)

                image_url = image_scrapper.find_image_urls(query_str)

                if num_local_scraped % 20 == 0:
                    print("Thread {} found {} for {}".format(
                        pid, image_url, query_str))

                write_lock.acquire()
                self.author_id_to_url[curr_author_id] = image_url
                write_lock.release()

            pbar.update(1)
            num_local_scraped += 1

            if num_local_scraped % 40 == 0:
                image_scrapper.reinitialize_driver()

        image_scrapper.close_driver()

def parse_args():
    parser = argparse.ArgumentParser(description="Run baselines.")

    parser.add_argument('--db_config', type=str,
                        help='Path to database config json file.')
    parser.add_argument('--num_threads', type=int,
                        help='Number of threads to use.')
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

    author_image_scraper = AuthorProfileImageScraper()
    author_image_scraper.update_authors_with_missing_photo(cursor)
    print('Missing Author image list updated')

    # Main program params
    num_threads = args.num_threads if(args.num_threads) else 6
    task_lock = threading.Lock()
    write_lock = threading.Lock()

    threads = []
    pbar = tqdm(total=len(author_image_scraper.get_author_ts()))

    # Starting threads
    for i in range(num_threads):
        curr_thread = threading.Thread(
            target=author_image_scraper.thread_search, args=(task_lock, write_lock, pbar))
        curr_thread.start()
        threads.append(curr_thread)

    # Waiting for threads to finish
    for thread in threads:
        thread.join()

    print("Done acquiring photos. Writing to database...")

    # Updating database with photo url entries
    for id, photo_url in author_image_scraper.get_author_id_to_url().items():
        if photo_url is None:
            continue

        update_sql = """
        UPDATE Author
        SET photo_url=%s
        WHERE id=%s
        """
        update_params = (photo_url, id)
        cursor.execute(update_sql, update_params)

    cursor.close()
    db.commit()
    pbar.close()

    # storing the results to a file
    if(args.store_results_to_file):
        with open(args.store_results_to_file, 'w') as f:
            f.write('AuthorId, PhotoUrl\n')
            for id, photo_url in author_image_scraper.get_author_id_to_url().items():
                f.write(f'{id}, {photo_url}\n')
