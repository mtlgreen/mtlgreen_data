#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup

file_root='./'

# Naming Scheme:
# get_... for GET Requests
# gets_... for multiple GET Requests
# write_... for file writing
# read_... for file reading
# parse_... for converting HTML data into python data structures
# scrape_... for the main process of obtaining data from source

def get_map(username=None,password=None):
    """GET Request for the volunteer map on simplyk"""
    s = requests.Session()
    r = s.get('https://www.simplyk.io/')
    if username == None or password == None:
        r = s.get('https://www.simplyk.io/landing/map')
    else:
        r = s.post('https://www.simplyk.io/login',data={'email':username,'password':password})
        r = s.get('https://www.simplyk.io/volunteer/map')
    return r

def write_map(r,filename='simplyk_requests.html'):
    """Saving the content of a request object as simplyk_requests.html for repeated usage"""
    with open(file_root+filename,'w') as f:
        f.write(r.content)

def read_map(filename='simplyk_requests.html'):
    """Reading the content from simplyk_requests.html as a request object for reapeated usage"""
    content = ''
    with open(file_root+filename,'r') as f:
        content = f.read()
    return content

def gets_events_data(event_ids=[]):
    # Multiple GET Requests to the events with the given ids
    s = requests.Session()
    for event_id in event_ids:
        r = s.get('https://www.simplyk.io/event/'+event_id)
        yield parse_event_content(r.content)

def parse_event_content(content):
    b = BeautifulSoup(content,features='html5lib')
    root = 'https://www.simplyk.io'
    def select_text(css,index):
        try:
            return b.select(css)[index].text
        except:
            return ''
    def select_attr(css,index,attr='href'):
        try:
            return b.select(css)[index].attrs[attr]
        except:
            return ''
    return {
        'org_title':select_text('div div div h4.mb a',0),
        'org_link': root + select_attr('div div div h4.mb a',0),
        'org_website':select_attr('div.col-md-4 a',0),
        'title':select_text('div div div h1 b',0),
        'subtitle':select_text('div div div h4.mt',0),
        'views' : select_text('div div div div div div.info__item',0),
        'address': select_text('div div div div div div.info__item',1),
        'age_requirement': select_text('div div div div div div.info__item',2),
        'description':select_text('div.align-paragraph',0),
        }

def write_scrape_tocsv(events_data,filename='event_data.csv'):

    # events_data = scrape() # Can be generator, iterator, or list

    import csv
    with open(file_root+filename,'w') as f:
        c = csv.writer(f)
        first = True
        l = []
        for event_data in events_data:
            if first:
                l = [ i for i in list(event_data.keys())]
                try:
                    c.writerow(l)
                except TypeError:
                    print(l)
                first = False
            c.writerow([ str(ascii_process(event_data[key])) for key in l ])

def ascii_process(text):
    if True:
        return text
    elif type(text) == bytes:
        return text.decode('utf-8')
    else:
        return text.encode('utf-8')

def scrape( username=None, password=None, to_csv=False, use_saved_map=False, cache_map=False, read_file='simplyk_requests.html',write_file='simplyk_requests.html' ):
    """Scrapes simplyk.io volunteering map for volunteer opportunities called 'events' here.  
    Optional arguments allow for saving/using cached versions of volunteering maps and optionally using simplyk username and password
    
    Returns a Generator Object.  Can use list(scrape()) to create a list version (takes a while to scrape through the whole map)
    
    Keyword arugments:
    username -- Simplyk login that provides some volunteer search criteria that can't be changed 
        without it. must also provide a `password`.
    password -- 
    to_csv -- saves result as csv file if set to True (default False)
    use_saved_map -- reads from the simplyk map html file specified by `read_file`
    cache_map -- saves map to file specified by `write_file` when set to True (default False)
    read_file -- the html file that will be read from which should contain a simplyk map
    write_file -- the filename that the simplyk map will be saved to
    """

    content = None # contains the simplyk map HTML content that will be parsed
    if not use_saved_map: # Downloads current map from the website
        r = get_map(username=username,password=password)
        content = r.content
        if cache_map: # Saves the current map from the website
            write_map(r,write_file)
    else: # Reads simplyk map from file
        content = read_map(read_file)

    b = BeautifulSoup(content,features='html5lib')
    items = b.select('li.list-group-item')
    item_ids = [ item.attrs['data-actid'] for item in items if 'data-actid' in item.attrs ]
    
    result = gets_events_data(item_ids)

    if to_csv:
        timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M'))
        default_name = 'simplyk_data_{}'.format(timestamp)
        write_data_to_csv(result,filename=default_name)

    return result # Returns a Generator Object

if __name__=='__main__':
    s = scrape()
    print(s)
    write_data_to_csv(s,'events_data.csv')