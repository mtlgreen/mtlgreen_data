#!/usr/bin/python3
import getpass,requests,json,csv, sys
try:
    import urllib.parse as urllib
except ImportError:
    import urllib
from bs4 import BeautifulSoup

# Local Reach, Montreal, Small, Medium,  Community Engagement, Ecosystem Maps, Google "Partnership Strategies", Check for Overlaps, Categorize
# Benchmarking, Analyze and Insight, Thematic, Green Purpose? Materials, Compost, Restoration, Recycling, Resilient Cities, Food Systems, Healthy Cities
# Transportation, Energy Usage,

# get_... for GET Requests
# gets_... for multiple GET Request
# write_... for file writing
# read_... for file reading
# parse_... for converting HTML data into python data structures
# scrape_... for the main process of obtaining data from source


# selenium is necessary for retrieving the cookies to authenticate requests to impak's api
# pip install selenium
# also download the 'chromedriver' that selenium wants you to download

def write_cookie(d,filename='cookies.json'):
    with open(filename,'w') as f:
        json.dump(d,f) # dumping the cookies into a cookies.json for later use

def read_scrape_json(filename='impak-data_eco.json'):
    try: # loading the data from the cookies.json
        f = open(filename,'r')
        result = json.load(f)
        # print(result)
        f.close()
        return result['results']
    except FileNotFoundError:
        print('make sure '+filename+' is in the same directory')
        return None
    except:
        print('ERROR: could not read file: '+filename)
        return None

def read_cookie(filename='cookies.json'):
    try: # loading the data from the cookies.json
        f = open(filename,'r')
        result = json.load(f)
        # print('cookie: ',result)
        f.close()
        cookies = requests.cookies.cookiejar_from_dict(result)
        return cookies
    except FileNotFoundError:
        print('make sure '+filename+' is in the same directory')
        return None
    except:
        print('could not read cookie file: '+filename)
        return None

def selenium_cookie_retrieval(username=None,password=None):
    # def prepare_driver_file():

    # try:
    #     import selenium
    # except ImportError:
    #     ans = input("This cookie retrieval process requires installation of selenium, \nand the downloading of a driver for your specific machine and browser. Do You Wish To Continue (y/n)? [y:default]")
    #     if ans=='n':
    #         pass
    #     else:
    #         return
    #     import pip.__main__ as m
    #     if 0==m._main("install --user selenium"):
    #         pass
    #     else:
    #         print("Could not install selenium aborting.")
    #         return
    
    # driver_type = prepare_driver_file()
    
    from selenium.webdriver.common.keys import Keys
    from selenium import webdriver

    if username == None:
        username = input('Enter your impak username: ')
    if password == None:
        password = getpass.getpass('Enter your impak password for {}: '.format(username))

    driver = webdriver.Chrome()
    # driver = webdriver.Firefox() # download the 'geckodriver' for this one
    driver.get('https://www.impak.eco/en/')
        
    # ---Logging In Code---
    element = driver.find_element_by_xpath('//*[@id="navbar-menu"]/ul[2]/li[2]/a')
    element.click()
    element = driver.find_element_by_xpath('//*[@id="id_username"]')
    element.send_keys(username)
    element = driver.find_element_by_xpath('//*[@id="id_password"]')
    element.send_keys(password)
    driver.find_element_by_xpath('//*[@id="form_signing_auth"]/div[3]/button').click()

    # ---Cookies Code---
    cookies = driver.get_cookies()
    driver.close()

    result = dict(zip([ c['name'] for c in cookies ],[ c['value'] for c in cookies]))
    return result

def requests_cookie_retrieval(username=None,password=None):
    s = requests.Session()
    headers = {}
    cookies=None

    if username == None:
        username = input('Enter your impak username: ')
    if password == None:
        password = getpass.getpass('Enter your impak password for {}: '.format(username))
    r = s.get('https://impak.eco/en/signin',headers=headers,cookies=cookies)
    # r = s.get('https://id.impak.eco/signin/?next=/a/authorize%3Fresponse_type%3Dcode%26scope%3Dopenid%2Bemail%2Bprofile%2Bstaffstatus%2Bsessionlocation%26client_id%3D669136%26nonce%3DoNUlgMuQe7jUp3zTxFyvCR6V6lmdWXpy%26lang%3Den%26state%3DqcW3NJTakWLOcvEkFyp23XIi7ffbYegp%26redirect_uri%3Dhttps%253A%252F%252Fwww.impak.eco%252Foidc%252Fauth%252Fcb%252F')
    b = BeautifulSoup(r.content,features='html5lib')
    csrf = b.select('#form_signing_auth > input[type="hidden"]')[0].attrs['value']

    headers = r.headers
    headers['Referer']=r.request.url
    cookies = r.cookies

    r1 = s.post('https://www.impak.eco'+urllib.unquote(r.url[34]),headers=headers,cookies=cookies, data={
        'csrfmiddlewaretoken':r.cookies.get_dict()['csrftoken'],
        'sign_in_view-current_step':'auth',
        'username':username,
        'password':password,
        })
    c = (s.cookies.get_dict(domain='www.impak.eco'))
    c.update( s.cookies.get_dict(domain='id.impak.eco'))
    c.update(s.cookies.get_dict(domain='=.impak.eco'))
    return s.cookies.get_dict()

def get_search_query(query='',debug=False,cookies=None):
    r = requests.get('https://www.impak.eco/api/v1/catalog/?q='+query+'&page_size=1&page=1&exclude=5f670987-3c36-4d03-a81c-c6be7d1ca49f',cookies=cookies)
    if debug: print(r.content)
    total_count = r.json()['metadata']['total_count']
    base_url = 'https://www.impak.eco/api/v1/catalog/?q='+query+'&page_size='+str(total_count)+'&exclude=5f670987-3c36-4d03-a81c-c6be7d1ca49f'
    first_set = r.json()
    r = requests.get(base_url,cookies=cookies)
    results = []
    print("Downloading pages of data: ")
    for i in range(1,first_set['num_pages']+1):
        r = requests.get(base_url+'&page='+str(i),cookies=cookies)
        print('Page',str(i)+':',r.url)
        try:
            results += r.json()['results']
        except:
            break
    return results

def write_scrape_tojson(query_name,scrape_results):
    import datetime
    timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M'))
    filename = 'impak-data_{}_{}.json'.format(query_name,timestamp)
    with open(filename,'w') as f:
        json.dump({'timestamp':str(datetime.datetime.now()),'results':scrape_results},f)

def write_scrape_tocsv(query_name,scrape_results):
    timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M'))
    filename = 'impak-data_{}_{}.csv'.format(query_name,timestamp)
    with open(filename,'w') as f:
        c = csv.writer(f)
        keys = ['name','username','phonenumber','categories','formatted_address','short_description','city','province','zip_code','country','website_url','current_step','profile_picture_url','background_picture_url','facebook_url','linkedin_url','point','twitter_url','is_author_affiliated','updated','id','instagram_url','route','is_online_only','created','background_square_picture_url','street_number']
        # keys = list( set(keys) | set(results[0].keys()) )
        c.writerow(keys)
        for d in scrape_results:
            points = []
            for key in keys:
                try:
                    point = d[key]
                    if key=='categories':
                        point = '|'.join([ str(category['name'])+';'+str(category['identifier'])+';'+str(category['level']) for category in point ])
                    elif key=='point':
                        point = ';'.join([ str(point[k]) for k in ['lng','lat'] ])
                    points.append(point)
                except:
                    points.append('')
            c.writerow(points)

def search_scrape_data(process_organization,scrape_results, **kwargs):
    
    for organization in scrape_results:
        filter_keys = list(set(kwargs) & set(organization))
        filter_positive = True
        for key in filter_keys:
            filter_positive = filter_positive and ()
                
        yield process_organization(organization)

def scrape(username=None,password=None,query='eco',to_csv=False,to_json=False,cookies_dict=None,cookies_source='',cookie_read_name='cookies.json',cookie_write_name=''):
    """Scrapes impak.eco companies' profiles that match a given query. 
    Returns a large list of the companies, might be a few thousand entries at a time.
    
    By default, scrape() with no parameters uses the query 'eco', and 
        reads the cookies from a file named 'cookies.json' which should be 
        in the current working directory

    Example usages:

    To set the query parameter to search for something different
        scrape(query='green')

    If we want to scrape simplyk and also use a new set of cookies, we name the cookies_source
        scrape(cookies_source='selenium') # could use 'requests' instead, but that one doesn't work
        # It will prompt you for username and password, unless you pass them in as parameters:
        scrape(username='jytiens@mtlgreen.com',cookies_source='selenium')

    To read cookies from file (not named cookies.json):
        scrape(cookie_read_name='c135.json')
    
    Set "to_csv" and/or "to_json" to True in any situation to output a file version of the results
        scrape(to_csv=True,to_json=True)
    """

    result = {}
    h_cookies = None # the actual dictionary that contains the cookies
    if cookies_dict is not None: # prioritize the cookies parameter
        h_cookies = cookies_dict
    elif cookies_source != '': # can place a string selenium or requests to use the default cookies retrieval method
        if cookies_source == 'selenium':
            h_cookies = selenium_cookie_retrieval(username,password)
        elif cookies_source == 'requests':
            h_cookies = requests_cookie_retrieval(username,password)
        else: # if somebody didn't put a valid string option
            raise ValueError('Not a valid source of cookies')
            return
    else: # by default, look for a file named cookies.json
        h_cookies = read_cookie(cookie_read_name)
        if h_cookies is None:
            return

    if cookie_write_name != '':
        write_cookie(h_cookies,cookie_write_name)

    result = get_search_query(query=query,debug=False,cookies=h_cookies) # Uncomment this if you don't want to use command line arguments
    
    # exit(0) # Uncomment this too ^

    # if len(sys.argv)>1:
    #     get_search_query(sys.argv[1])
    # else:
    #     print('run this python script using python 3 like "python3 impak_api.py eco" to search for "eco" ')

    if to_json:
        write_scrape_tojson(query,result)
    if to_csv:
        write_scrape_tocsv(query,result)
    return result
if __name__=='__main__':
    """I wrote code here occassionally to test out the methods while writing them"""
    # scrape()
    result = read_scrape_json('impak-data_eco.json')
    # s = search_scrape_data(lambda x : (x['name'], x['short_description']),result,country='CA')
