from selenium import webdriver
import time
 
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
options.binary_location = "C:\Program Files (x86)\Chromium\Application\chrome.exe"
driver = webdriver.Chrome(chrome_options=options)
driver.get('https://python.org')