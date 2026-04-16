import requests
import time
from multiprocessing import Pool, cpu_count
from collections import Counter


# Configuration
# The server's public IP address
BASE_URL = "http://72.60.221.150:8080"
STUDENT_ID = "MDS202532"


def mapper(filename_chunk):
    secret_key = login_and_get_secret_key()
    first_words = []

    chunk_id = filename_chunk[0]
    print(f'Chunk - id {chunk_id} -- started')

    for filename in filename_chunk:
        title = get_publication_title(secret_key, filename)
        first_words.append(title.strip().split()[0])

    print(f'Chunk - id {chunk_id} -- ended')
    return Counter(first_words)


def login_and_get_secret_key():
    r = requests.post(
        BASE_URL + '/login',
        json={'student_id': STUDENT_ID}
    )

    return r.json()['secret_key']


def get_publication_title(secret_key, filename):
    max_retries = 10
    sleep_time = 0.5

    for _ in range(max_retries):

        try:
            r = requests.post(
                BASE_URL + '/lookup', 
                json={'secret_key': secret_key, 'filename': filename},
            )

            status_code = r.status_code

            # All OK
            if status_code == 200:
                sleep_time = 0.5
                return r.json()['title']
            
            # Too many requests error
            if status_code == 429:
                print(f'Too many requests for filename {filename}')
                time.sleep(sleep_time)
                sleep_time *= 2
                continue
        
        except Exception as e:
            print(f'Something went wrong with filename {filename} --- {e}')
            time.sleep(5)
            continue
    

    raise Exception("Too many retires")


def verify_top_10(top_10_list):
    secret_key = login_and_get_secret_key()
    r = requests.post(
        BASE_URL + '/verify',
        json={'secret_key': secret_key, 'top_10': top_10_list}
    )

    print(r.json())


if __name__ == "__main__":
    chunks = []
    for i in range(20):
        chunk = []
        for j in range(50):
            file_number = i*50 + j
            chunk.append(f"pub_{file_number}.txt")
        chunks.append(chunk)

    with Pool(processes=5) as pool:
        results = pool.map(mapper, chunks)

    c = Counter()
    for i in range(20):
        c += results[i]

    top_10 = [title for title, _ in c.most_common(10)]

    if top_10:
        verify_top_10(top_10)



