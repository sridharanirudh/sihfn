import argparse
import twarc
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('auth_file')
args = parser.parse_args()

with open(args.auth_file, 'r') as file_data:
    KEYS = yaml.safe_load(file_data)

t = twarc.Twarc(KEYS['CONSUMER_API_KEY'], KEYS['CONSUMER_SECRET_KEY'],
                KEYS['ACCESS_TOKEN'], KEYS['ACCESS_TOKEN_SECRET'])
