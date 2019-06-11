#!/usr/bin/env python3
# coding=utf-8

import sys, getopt
import requests
import csv
import argparse
from termcolor import colored, cprint
import time

startTime = time.time()

url = 'https://rejestr.io/api/v1/krs' # see docs at https://rejestr.io/api-krs

parser = argparse.ArgumentParser(
    description='KRS data fetching script powered by the rejestr.io API')
parser.add_argument(
    '-p', '--page',
    nargs=1,
    default=1,
    help='starting page for API request'
)
parser.add_argument('-r', '--registry', nargs=1, default='NGO')
parser.add_argument('-c', '--city', nargs=1, default=u'Poznań')
parser.add_argument('output_file')

args = vars( parser.parse_args( sys.argv[1:]) )

params = {
    'per_page': 100, # this is the max for the API
    'page': int( args['page'][0] )
}

output_file = args['output_file'][0]

filter_registry = args['registry'][0]
filter_city = args['city'][0]
total_orgs = 0

# @todo add error/exception handling for entire script

while total_orgs == 0 or ( params['page'] * params['per_page'] ) < total_orgs:
    print( 'Connecting to Rejestr.io to fetch page', params['page'], end='' )
    r = requests.get( url, params=params )

    # @todo add request error handling
    cprint( ' [{}]'.format(r.status_code), 'green' )
    r = r.json()

    if total_orgs == 0:
            total_orgs = r['total']
            print('Found {} organizations.'.format(total_orgs))

    for item in r['items']:
        org = item['data']
        if (org['registry'] == filter_registry
            and
            org.get( 'address' )
            and
            org['address']['city'] == filter_city ):
            # @todo filter unions, business federations and other not-quite-ngos

            # write to file
            cprint( 'Match! Saving {} to file.'.format(org['name']), 'green')
            save = [
                org['name'].encode('utf-8'),
                org['id'],
                org['legal_form'].encode('utf-8'),
                org['regon'],
                org['nip'],
                org['address']['street'].encode('utf-8'),
                org['address']['house_no'],
                org['address']['apt_no'],
                org['address']['code'],
                org['removed'],
                org['first_entry_date'],
                org['last_entry_date']
            ]
            with open( output_file, mode='a+', encoding='utf-8' ) as csv_file:
                org_writer = csv.writer(csv_file)
                org_writer.writerow( save )

    params['page'] += 1

# output runtime for script
print('Execution time: {0} seconds'.format(time.time() - startTime))
print('Processed pages {} through {}'.format(args['page'][0],params['page']))
print('To start at the last fetched page, run: ./krs-fetcher.py -p {}'.format(params['page']))
