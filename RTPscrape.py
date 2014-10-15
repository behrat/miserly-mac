import csv
import urllib
import datetime
import dateutil.parser
from bs4 import BeautifulSoup
opener = urllib.FancyURLopener()

def get_prices_for_day(querydate):
    """
    Returns an iterator of (datetime_starting, price) pairs.
    """
    datestring = "%02d/%02d/%d" % (querydate.month, querydate.day, querydate.year)

    download_url = \
            "https://www2.ameren.com/RetailEnergy/rtpDownload.aspx?Company=19&Date=%s&ptype=D" \
             % datestring 
    
    f = opener.open(download_url)
    
    soup = BeautifulSoup(f)
    viewstate = soup.select("#__VIEWSTATE")[0]['value']
    eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']
    
    formData = (
        ('__EVENTVALIDATION', eventvalidation),
        ('__VIEWSTATE', viewstate),
        ('ctl00$ContentPlaceHolder1$CompanyCode', '19'),
        ('ctl00$ContentPlaceHolder1$ccFromDate', datestring),
        ('ctl00$ContentPlaceHolder1$ccToDate', datestring),
        ('ctl00$ContentPlaceHolder1$btnSubmit.x', "87"),
        ('ctl00$ContentPlaceHolder1$btnSubmit.y', '9'),
    )
    encodedFields = urllib.urlencode(formData)
    
    f = opener.open(download_url, encodedFields)
    
    rtpreader = csv.reader(f, delimiter=',')
    
    # remove column header
    rtpreader.next()

    for row in rtpreader:
        date_string = row[0]
        hour_ending = int(row[1])
        hour_starting = hour_ending - 1
        price = float(row[2])

        date = dateutil.parser.parse(date_string)
        datetime_starting = date + datetime.timedelta(hours=hour_starting)
        
        yield {"start": datetime_starting, "price": price}

