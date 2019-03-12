#!/usr/bin/python3
import getpass,requests,json,csv, sys
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
from bs4 import BeautifulSoup

# Naming Scheme:
# get_... for GET Requests
# gets_... for multiple GET Requests
# write_... for file writing
# read_... for file reading
# parse_... for converting HTML data into python data structures
# scrape_... for the main process of obtaining data from source

def get_hubs_list():
    """Grab the json file that lists the hubs for global shapers"""
    s = requests.Session()
    r1 = s.get('https://www.globalshapers.org/hubs.json')
    return r1.json()

