import sys
import csv
import urllib
import datetime
import subprocess
from bs4 import BeautifulSoup
opener = urllib.FancyURLopener()

now = datetime.datetime.now()
today = datetime.date.today()

if now.hour < 17: 
    querydate = today
else:
    querydate = today + datetime.timedelta(days=1)


datestring = "%02d/%02d/%d" % (querydate.month, querydate.day, querydate.year)

download_url = "https://www2.ameren.com/RetailEnergy/rtpDownload.aspx?Company=19&Date=%s&ptype=D" % datestring 

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

price_cutoff = .040

sleeping = False

# column header
print rtpreader.next()

for row in rtpreader:

    hour_ending = int(row[1])
    price = float(row[2])

    if not sleeping:
        if price > price_cutoff:
            sleeping = True
            # TODO: handing beginning of day
            print "Scheduling Sleep"
            subprocess.call('pmset schedule sleep "%s %d:48:00 2>&1"' % (datestring, hour_ending-2), shell=True)

    if sleeping:
        if price < price_cutoff:
            sleeping = False
            print "Scheduleing Wake"
            subprocess.call('pmset schedule wake "%s %d:01:00 2>&1"' % (datestring, hour_ending-1), shell=True)

    print row

subprocess.call('pmset -g sched', shell=True)
