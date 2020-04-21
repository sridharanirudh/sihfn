import json
import argparse
import requests
import urllib.parse
from requests_oauthlib import OAuth1
import yaml
import pandas as pd
from time import sleep
import gzip

TWURL = 'https://api.twitter.com/1.1'
SUCCESS_RESPONSE_CODE = 200

parser = argparse.ArgumentParser()
parser.add_argument('auth_file')
args = parser.parse_args()


class LimitReachedError(Exception):
    def __init__(self):
        super().__init__('Rate Limit Reached')


class NoTweetsFetchedError(Exception):
    def __init__(self):
        super().__init__('No Tweets Fetched')


def create_auth_token():
    with open(args.auth_file, 'r') as file_data:
        KEYS = yaml.safe_load(file_data)
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    auth = OAuth1(KEYS['CONSUMER_API_KEY'], KEYS['CONSUMER_SECRET_KEY'],
                  KEYS['ACCESS_TOKEN'], KEYS['ACCESS_TOKEN_SECRET'])
    r = requests.get(url, auth=auth)
    print(f'Auth Request {r}')
    return auth


def rate_limit_handler(status_code, remaining, reset):
    reset = pd.to_datetime(reset, unit='s', utc=True)
    time_now = pd.Timestamp.now(tz='UTC')
    reset_in = int((reset - time_now).total_seconds()) + 5
    if status_code != SUCCESS_RESPONSE_CODE or int(remaining) < 10:
        print('Reset In', reset_in)
        sleep(reset_in)
    else:
        sleep(5)


def fetch_tweets(screen_name, auth, count=None, since_id=None, max_id=None,
                 tries=2):
    if tries == 0:
        raise NoTweetsFetchedError()
    try:
        query = {
            'screen_name': screen_name,
            'include_rts': True,
            'tweet_mode': 'extended'
        }
        if max_id:
            query['max_id'] = str(max_id)
        if since_id:
            query['since_id'] = str(since_id)
        if count:
            query['count'] = count
        qstr = urllib.parse.urlencode(query)
        res = requests.get(f'{TWURL}/statuses/user_timeline.json?{qstr}',
                           auth=auth)
        data = json.loads(res.text)
        if len(data) == 0:
            raise NoTweetsFetchedError()
        return data, str(data[0]['id']), str(data[-1]['id']), res
    except LimitReachedError:
        print(f'{screen_name} {tries} LRE')
        rate_limit_handler(res.status_code,
                           res.headers['x-rate-limit-remaining'],
                           res.headers['x-rate-limit-reset'])
        tries -= 1
        fetch_tweets(screen_name, auth, count, since_id, max_id, tries)


def write_to_file(fname, data):
    f = gzip.open(fname, 'wb')
    f.write(json.dumps(data).encode('utf-8'))
    f.close()


auth_token = create_auth_token()
outlets = ['CDNNow', 'ABCPolitics', 'CNNPolitics', 'OccupyDemocrats',
           'politico', 'johnhawkinsrwn', 'other98', 'AlterNet', 'OANN',
           'foxnewspolitics']
for outlet in outlets:
    reqd_tweets = 2000
    last_id = None
    results = []
    while reqd_tweets > 0:
        try:
            tweets, first_id, last_id, res = fetch_tweets(outlet, auth_token, 200,
                                                          None, last_id)
            results.extend(tweets)
            reqd_tweets -= len(tweets)
            rate_limit_handler(res.status_code,
                               res.headers['x-rate-limit-remaining'],
                               res.headers['x-rate-limit-reset'])
        except NoTweetsFetchedError:
            print(f'{outlet} NTFE')
            break
        write_to_file(f'tweets/{outlet}.json.gz', results)
        print(f'Done {outlet} {len(results)}')
