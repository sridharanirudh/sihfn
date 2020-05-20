import requests
import json
import gzip
from pathlib import Path
import logging
import glob
from requests.exceptions import Timeout

logging.basicConfig(filename='logs/articles.log', filemode='a+',
                    level=logging.DEBUG)

files = glob.glob("data/tweets/*")
files = ['data/tweets/AlterNet.json.gz']

for fname in files:
    outlet = fname.split('/')[-1].split('.')[0]
    folder_name = f'data/articles/{outlet}'
    logging.info(f'Started {fname}')
    Path(folder_name).mkdir(parents=True, exist_ok=True)
    f = gzip.open(fname, 'r')
    tweets = json.loads(f.read())
    t = 0
    for tweet in tweets:
        urls = tweet['entities']['urls']
        logging.info(f'Started {fname} - tweet - {tweet["id"]} - {len(urls)} - Started')
        if len(urls) > 0:
            i = 0
            for url in urls:
                eurl = url['expanded_url']
                logging.info(f'{outlet} - {eurl}')
                try:
                    res = requests.get(eurl, timeout=30)
                    a = open(f'{folder_name}/{tweet["id"]}-{i}', 'w')
                    a.write(res.text)
                    logging.info(f'{outlet} - {eurl} - done - {t}')
                    t += 1
                except Timeout:
                    logging.error(f'{outlet} - {eurl} - {res.status_code} - failed')
                i += 1
        logging.info(f'Started {fname} - tweet - {tweet["id"]} - End')
        t += 1
    f.close()
