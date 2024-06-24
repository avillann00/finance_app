# import requests to access api info
import requests
# import time to pause the loop
import time

# gets the stock prices
def get_stocks():

    # api key
    KEY = 'NC95CRWJ2R1U0MV4'
    # ticker symbols
    tickers = ['APPL', 'AMZN', 'NVDA', 'CMG', 'TSLA']
    # the tickers and their closing price
    info = {}

    # loop through each ticker
    for ticker in tickers:
        # api url
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={KEY}'
        
        # raw api response
        response = requests.get(url)

        # error checking
        if response.status_code == 200:
            # change into json format
            data = response.json()
            
            # ensure 'Time Series (Daily)' key is in data
            if 'Time Series (Daily)' in data:
                # the stocks latest date
                latest_date = list(data['Time Series (Daily)'].keys())[0]
                # the stocks closing price on that date
                closing_price = data['Time Series (Daily)'][latest_date]['4. close']
                
                # add to dictionary
                info[ticker] = closing_price
            else:
                # date/price is not in api for that ticker
                print(f'Error: "Time Series (Daily)" not found in response for {ticker}')
        else:
            # print the error code
            print(f'Error: {response.status_code} for ticker {ticker}')

    # sleep to avoid hitting api rate limits
    time.sleep(120)

    # return all of the data
    return info
