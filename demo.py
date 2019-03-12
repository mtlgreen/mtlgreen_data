from mtlgreen_data import impak_scraper as impak
from mtlgreen_data import simplyk_scraper as simplyk
# Should use python 3. Probably won't work with python 2.
# Open with `python3 -i demo.py` to check out the data that was grabbed

# Impak gives company profiles (names, descriptions, their websites)
impak_results = impak.scrape(cookie_read_name='cookies.json',query='eco',to_csv=False,to_json=False)

# print('Impak Example Data: ',impak_results[0])

# Simplyk gives data on volunteering opportunities
simplyk_results = (simplyk.scrape(to_csv=False)) # Simplyk doesn't require any cookies

# print('Simplyk Example Data: ',list(simplyk_results)[0])