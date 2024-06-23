# import requests to access api info
import requests

# gets the exchange rates
def get_rates():
    # api key
    KEY = 'e4d012dbee004a99b7c642269072cb33'
    # api url
    url = f'https://openexchangerates.org/api/latest.json?app_id={KEY}'
    # all of the currencies
    currencies = ['CAD', 'USD', 'EUR', 'JPY', 'PHP']
    # currencies and their rates
    info = {}

    # get the raw api response
    response = requests.get(url)
    
    # error checking
    if response.status_code == 200:
        # change into json format
        data = response.json()

        # loop through each currency and get the exchange rate
        for currency in currencies:
            # if currency is in api
            if currency in data['rates']:
                # get the rate
                exchange_rate = data['rates'][currency]

                # add to dictionary
                info[currency] = exchange_rate
            # currency not in api
            else:
                print(f'Currency {currency} not found in the response.')
    else:
        # print the error code
        print(f'Error: {response.status_code}')

    # return all of the data
    return info
