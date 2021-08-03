import requests
import math


# Get stock quote data from Finnhub API
def quoteData(symbol):
  url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      return data
    else:
      return 'empty data'


# Get basic financials data from Finnhub API
def financesData(symbol):
  url = f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data["metric"]:
      return data["metric"]
    else:
      return 'empty data'


# Get company profile data from Finnhub API
def companyData(symbol):
  url = f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      return data
    else:
      return 'empty data'


# Get company overview data from Alphavantage API
def companyOverviewData(symbol):
  url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey=1ZZ8Y4Y0A7I7TSAP'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    data = r.json()
    if data:
      if "Note" in data.keys():
        return 'empty data'
      else:
        return data
    else:
      return 'empty data'


# Get information about stock volume from Alphavantage API
def volumeData(symbol):
  url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=c3nlhsaad3iabnjjd4c0'
  r = requests.get(url)
  status = r.status_code
  if status != 200:
    return 'error'
  else:
    # Check if data is available for the stock symbol
    data = r.json()
    if data:
      if "Note" in data.keys():
        return 'empty data'
      elif data["Global Quote"]:
        return data["Global Quote"]
      else:
        return 'empty data'
    else:
      return 'empty data'


# Round number to two decimal places
def twoDecPlaces(value):
  if value:
    result = "{:.2f}".format(float(value))

    return result
  else:
    return value


# Shorten extremely large numbers
def millify(value):
  millnames = ['','k','M','B','T']
  if value:
    n = float(value)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.2f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
  else:
    return value