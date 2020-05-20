import argparse
import os
import requests
from requests_oauthlib import OAuth1
import yaml
import json
import urllib.parse
import pdb
from time import sleep
import gzip

parser = argparse.ArgumentParser()
parser.add_argument('auth_file')
args = parser.parse_args()


def create_auth_token():
    with open(args.auth_file, 'r') as file_data:
        KEYS = yaml.safe_load(file_data)
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        auth = OAuth1(KEYS['CONSUMER_API_KEY'], KEYS['CONSUMER_SECRET_KEY'], KEYS['ACCESS_TOKEN'], KEYS['ACCESS_TOKEN_SECRET'])
        r = requests.get(url, auth=auth)
        print(r)
        return auth


auth = create_auth_token()
s = requests.Session()
url = "https://stream.twitter.com/1.1/statuses/filter.json"
query = {'track': ['covid19', 'covid', 'coronavirus']}
qstr = urllib.parse.urlencode(query)
with s.get(f'{url}?{qstr}', auth=auth, stream=True) as resp:
    print(resp)
    pdb.set_trace()
