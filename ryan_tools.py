import pandas as pd
import seaborn as sea
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as date_parse
import csv
import calendar

def mround( number, by = 2 ):
    return round( number, by )

def find_column_id(findme , row ):
    iterator = 0
    while ( iterator < len(row) ):
        if  (findme.lower() in row[iterator].lower()) :
            return iterator
        iterator = iterator + 1
    return False

def get_month( datetime):
    return datetime.strftime("%B")

        
def read_date(text):
    text = text.strip('\'')
    text = text.strip('\"')
    for fmt in ( '%m/%d/%y' , '%M/%D/%y' , '%m/%d/%Y', '%Y/%m/%d', '%Y/%M/%D', 'Report Date :%m/%d/%Y', '%Y%M%D' , '%Y%m%d', '%M/%D/%y %H:%M:%S %p', '%m/%d/%Y %H:%M:%S %p'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            return date_parse(text)            
            pass
    raise ValueError('No Valid Date found in :' + str(text))


def get_date_str(date, sep ='/'):
    try:
        return str(date.month) + sep + str(date.day) + sep + str(date.year)
    except AttributeError:
        return get_date_str(read_date(date), sep )

def s_s( number, spaces = 8 ):
    return ( str(number).ljust(spaces) )

def read_cash(text):
    text = str(text)
    if text == '':
        return 0
    temp = text.replace(' ', '')
    temp = text.replace(',', '')
    temp = temp.replace('$', '')

    if ('(' in temp or ')' in temp):
        temp = temp.replace('(', '')
        temp = temp.replace(')', '')
        ans = float(temp) * -1.0
        return ans
    ans = round(float(temp),2)
                
    return ans

def get( identity, item_list  ):
    
    for items in item_list:
        if items.id == identity:
            return items
        
def unix_time_millis(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000.0

def print_list(list_of_things):
    try:
        for items in list_of_things:
            items.print()
        return
    except AttributeError:
        for items in list_of_things:
            print(items)
  

def last_date_of_month(date_time):
    last = calendar.monthrange( date_time.year, date_time.month)[1]
    return datetime.datetime(date_time.year, date_time.month, last, 23, 59, 59, 999999 )

