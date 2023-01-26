from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import datetime
import time
import humanize
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set output destination folder
data_destination = str(Path.cwd() / "output")

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

options = webdriver.ChromeOptions()
prefs = {"download.default_directory" : data_destination}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(service=Service(""), options = options) # insert path to chromedriver


# Set date parameters: 
# 'O' for date incident occurred
# 'R' for date incident reported
# 'U' for date incident updated

date_type = 'O'
start_date_DDMMYYYY = '01012023'
end_date_DDMMYYYY = '01012023'

# Loading StEIS and passing credentials

driver.get('https://steis.improvement.nhs.uk/steis/untoward3.nsf/Reports2?openform')
driver.find_element(By.ID, 'un').send_keys('') # insert username
driver.find_element(By.ID, 'pwd').send_keys('' + Keys.ENTER) # insert password

# Select date type

if date_type == 'R':
    driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[3]/tbody/tr/td/label[1]').click()
elif date_type == 'O':
    driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[3]/tbody/tr/td/label[2]').click()
elif date_type == 'U':
    driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[3]/tbody/tr/td/label[3]').click()
else:
    print('ERROR: invalid date type')

# Pass start date

driver.find_element(by=By.NAME, value='sd1').clear()
driver.find_element(by=By.NAME, value='sd1').send_keys(start_date_DDMMYYYY[0:2])

driver.find_element(by=By.NAME, value='sd2').clear()
driver.find_element(by=By.NAME, value='sd2').send_keys(start_date_DDMMYYYY[2:4])

driver.find_element(by=By.NAME, value='sd3').clear()
driver.find_element(by=By.NAME, value='sd3').send_keys(start_date_DDMMYYYY[4:8])

# Pass end date

driver.find_element(by=By.NAME, value='ed1').clear()
driver.find_element(by=By.NAME, value='ed1').send_keys(end_date_DDMMYYYY[0:2])

driver.find_element(by=By.NAME, value='ed2').clear()
driver.find_element(by=By.NAME, value='ed2').send_keys(end_date_DDMMYYYY[2:4])

driver.find_element(by=By.NAME, value='ed3').clear()
driver.find_element(by=By.NAME, value='ed3').send_keys(end_date_DDMMYYYY[4:8])

# Save search

driver.find_element(by=By.CSS_SELECTOR, value="input[value='Save your search']").click();

# Hit ok on popup

driver.switch_to.alert.accept()

# Navigate to unprocessed
driver.get("https://steis.improvement.nhs.uk/steis/untoward3.nsf/SearchUnprocessed?openview")

# Grab most recent search details
search_created_on = driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[2]/tbody/tr[2]/td[1]').text
search_start = driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[2]/tbody/tr[2]/td[2]').text
search_end = driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[2]/tbody/tr[2]/td[3]').text
search_status = driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[2]/tbody/tr[2]/td[4]').text
query_element = driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/div/div/div/div[2]/div/table[2]/tbody/tr[2]/td[5]/a')
query_href = query_element.get_attribute('href')

# Check query is as expected - need to introduce an if here
print('Navigating to',
      search_status,
      'query created on',
      search_created_on,
      'for incidents from',
      search_start,
      'to',
      search_end,
      'at',
      query_href)


# Navigate to query page
query_element.click()

wait_start = datetime.datetime.now()
print('Starting check for CSV')
while True:
    print('Searching at',datetime.datetime.now())
    if driver.find_elements(by=By.XPATH, value='//*[@id="main-wrapper"]/a'):
        driver.find_element(by=By.XPATH, value='//*[@id="main-wrapper"]/a').click()
        wait_end = datetime.datetime.now()
        print('> Found CSV at', wait_end)
        print('> CSV saved to',data_destination)
        print('> Query took',humanize.naturaldelta(wait_end - wait_start))
        break
    else:
        print('> No element found, trying again in 5 minutes')
        driver.refresh()
        time.sleep(300)
        time_now = datetime.datetime.now()
        elapsed = time_now - wait_start
        if elapsed > datetime.timedelta(hours=8):
            print('> Search aborted, no element found after 8 hours. Check later at',query_href)
            break
