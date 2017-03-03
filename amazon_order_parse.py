import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException        
from ryan_tools import *
from xml.etree import ElementTree as et

import shutil
import glob
import datetime
import time

seller_id = 'None'
mws_auth_token = 'None'
aws_access_key_id = 'None'
secret_key = 'None'
market_place_id = 'None'
amazon_url = 'https://mws.amazonservices.com/scratchpad/index.html'

driver = None
def browser():
    global driver
    if driver == None:
        x = webdriver.Chrome()
        x.maximize_window()
        driver = x
        return x
    return driver
        
def __download_orders__(start_date, end_date, token ):
    first = token == mws_auth_token
    start_time = str(start_date.hour).zfill(2) + ':' + str(start_date.minute).zfill(2) + ':' + str(start_date.second).zfill(2)
    end_time  = str(end_date.hour).zfill(2) + ':' + str(end_date.minute).zfill(2) + ':' + str(end_date.second).zfill(2)
    start_date_str = str(start_date.year) + '-' + str(start_date.month).zfill(2) + '-' + str(start_date.day).zfill(2)
    end_date_str =  str(end_date.year) + '-' + str(end_date.month).zfill(2) + '-' + str(end_date.day).zfill(2)
            
    driver = browser()
    
    driver.get(amazon_url)

    x = driver.find_element_by_id('apisection')
    x.click()
    x.send_keys(Keys.ARROW_DOWN)
    x.send_keys(Keys.ARROW_DOWN)
    x.send_keys(Keys.ARROW_DOWN)
    x.send_keys(Keys.RETURN)
    x = driver.find_element_by_id('apicall')
    x.click()
    x.send_keys(Keys.ARROW_DOWN)
    if not first:
        x.send_keys(Keys.ARROW_DOWN)
        
    x.send_keys(Keys.ARROW_DOWN)
    x.send_keys(Keys.RETURN)
    
    driver.find_element_by_id('merchantID').send_keys(seller_id)
    driver.find_element_by_id('authToken').send_keys(mws_auth_token)
    driver.find_element_by_id('awsAccountID').send_keys(aws_access_key_id)
    driver.find_element_by_id('secretKey').send_keys(secret_key)
    
    if not first:
        driver.find_element_by_id('NextToken').send_keys(token)
    
    if first:
        driver.find_element_by_id('MarketplaceId.Id.-').send_keys(market_place_id)
        driver.find_element_by_id('CreatedAfter').send_keys(start_date_str)
        driver.find_element_by_id('apicall').click()
        driver.find_element_by_id('CreatedBefore').send_keys(end_date_str)
        
        driver.find_element_by_id('CreatedAfter_time').clear()
        driver.find_element_by_id('CreatedAfter_time').send_keys(start_time)
        driver.find_element_by_id('CreatedBefore_time').clear()
        driver.find_element_by_id('CreatedBefore_time').send_keys(end_time)
                                                        
        driver.find_element_by_id('MaxResultsPerPage').send_keys('100')

    driver.find_element_by_id('submit').click()
    response = ''
    while len(response) == 0:
        response = driver.find_element_by_id('response').text
    response = response.replace('&', 'and' )
    return response

def is_failed(response):
    root  = et.fromstring(response)
    if 'ErrorResponse' in root.tag:
        print('WAITING 60 Seconds FOR REFRESH')
        for num in range(1, 61):
            print( num, end = ' ' )
            time.sleep(1)
        return True
    return False

def download_orders(start_date, end_date, token):
    failed = True
    while failed:
        response = __download_orders__(start_date, end_date, token )
        failed = is_failed(response)
    #write_string(response)
    return response

def get_next_token(response):
    root  = et.fromstring(response)
    token = None
    for child in root:
        if 'ListOrders' in child.tag:
            for inner_child in child:
                if 'NextToken' in inner_child.tag:
                    token = inner_child.text    
    return token
    
def read_xml(response):   
    root  = et.fromstring(response)
    orders = False
    for child in root:
        if 'ListOrders' in child.tag:
            for inner_child in child:
                if 'Orders' in inner_child.tag and 'CreatedBefore' not in inner_child.tag and 'NextToken' not in inner_child.tag:
                    orders = inner_child
    data = pd.DataFrame()
    i = 0
    for order in orders:
    
        for detail in order.iter():
            column = detail.tag.split('}')[1]
            data.loc[i, column] = detail.text

        i = i + 1
                    
        
    for column in data.columns:
        if 'date' in column.lower():
            data[column] = pd.to_datetime(data[column])
            data[column] = data[column] - datetime.timedelta( hours = 7 )
    print('Downloaded ',len(data), ' Orders')
    return data
files = 0
def write_string(string):
    global files
    file = open('File No' + str(files) + '.xml', 'w' )
    files = files + 1
    file.write(string)
    file.close()
    
def full_download_orders(start_date, end_date, mws_auth_token):
    responses = []
    
    response_1 = download_orders( start_date, end_date, mws_auth_token)
    
    token = get_next_token(response_1)
    responses.append(read_xml(response_1))
    i = 0
    
    while (token != None):
        response = download_orders(start_date, end_date, token)
        responses.append( read_xml(response))
        i = i + 1
        token = get_next_token(response)
                          
    
    return pd.concat(responses)


    
start_date = read_date(input('Start_Date?\n'))
end_date = read_date(input('End_Date?\n'))

data = full_download_orders(start_date, end_date, mws_auth_token )
filename = getdate(start_date, sep = '_') + ' - '  + getdate(end_date, sep = '_') + 'Amzon Orders.csv'
data.to_csv(filename)
driver.close()
driver = None
