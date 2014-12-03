import urllib
import datetime
import dateutil.parser
from bs4 import BeautifulSoup
opener = urllib.FancyURLopener()

def get_prices_for_day(querydate):
    """
    Returns an iterator of (datetime_starting, price) pairs.
    """
    datestring = "%02d/%02d/%d" % (querydate.month, querydate.day, querydate.year        )


    download_url = "https://www2.ameren.com/RetailEnergy/RealTimePrices" 

    formData = (
        ('DateWanted', datestring),
        ('Type', 'DayAhead'),
    )

    encodedFields = urllib.urlencode(formData)
   
    f = opener.open(download_url, encodedFields)
    
    soup = BeautifulSoup(f)
    table = soup.find("table", {"class": "priceTable"})
    rows = table.find_all('tr')

    # remove column header
    rows = rows[1:]

    for row in rows:
        cols = row.find_all('td')

        date_string = cols[0].text
        hour_ending = int(cols[1].text.split()[2])
        hour_starting = hour_ending - 1
        price = float(cols[2].text)

        date = dateutil.parser.parse(date_string)
        datetime_starting = date + datetime.timedelta(hours=hour_starting)
        
        yield {"start": datetime_starting, "price": price}

