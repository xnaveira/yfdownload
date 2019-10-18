#!/usr/bin/env python

import os
import sys
import yaml

import certifi
import urllib3

from output import output_print, Level
from clint.arguments import Args

from scraper import YahooBackupScraper

if __name__ == '__main__':
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where(), timeout=4, retries=3)
    args = Args()

    output_print('Arguments: {}'.format(args.all))

    if len(args) < 1 or '-h' in args.flags:
        output_print('Use: yfdownload.py [-c file.yaml] name_of_the_group\n\
Put login: yourlogin and password: yourpassword in file.yaml', Level.ERROR)
        sys.exit(1)

    if '-c' in args.flags:
        config_file = dict(args.grouped)['-c'][0]
        output_print('Reading credentials from {}'.format(config_file))
        with open(config_file, 'r') as contents:
            config = yaml.load(contents, Loader=yaml.BaseLoader)
        yahoo_group = args.all[2]
        try:
            scraper = YahooBackupScraper(
                yahoo_group, driver='firefox',
                login_email=config['login'],
                password=config['password'])
        except KeyError:
            output_print('Error parsing config file', Level.ERROR)
            sys.exit(4)
    else:
        output_print(
            'Attempting download without credentials. If the group is private you need to create a yaml file with '
            'your credentials first.')
        yahoo_group = args.all[0]
        scraper = YahooBackupScraper(
            yahoo_group, driver='firefox')

    if os.path.exists(yahoo_group):
        output_print("Directory {} already exists remove or rename it and run again".format(yahoo_group), Level.WARNING)
        sys.exit(2)
    else:
        os.makedirs(yahoo_group)

    for file_info in scraper.yield_walk_files():
        output_print('Processing {}'.format(file_info['filePath']))
        if 'b#' not in file_info['filePath']: #Do not process the file if it is affected by the non ASCII chars bug
            if file_info['fileType'] == 'd':
                os.makedirs(yahoo_group + file_info['filePath'], exist_ok=True)
                output_print('{} created'.format(file_info['filePath']), Level.SUCCESS)
            elif file_info['fileType'] == 'f':
                r = http.request('GET', file_info['url'])
                open(yahoo_group + file_info['filePath'], 'wb').write(r.data)
                output_print('{} downloaded'.format(file_info['filePath']), Level.SUCCESS)
            else:
                output_print('Unknown type in file: {}'.format(file_info), Level.ERROR)
                sys.exit(3)
        else:
            output_print('Skipping {}'.format(file_info['filePath']), Level.WARNING)

    output_print("Done processing all files!", Level.SUCCESS)
