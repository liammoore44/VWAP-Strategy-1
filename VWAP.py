from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from collections import deque
from twilio.rest import Client
from config import *
from multiprocessing import Process
import multiprocessing
from itertools import product
import requests, json, collections
import time 
import pandas as pd
import matplotlib.pyplot as plt


headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": secret_key}
client = Client(twilio_sid, twilio_auth)

indicators = TechIndicators(alphavantage_key, output_format='pandas')
time_series_data = TimeSeries(alphavantage_key, output_format='pandas')


def get_clock():
    request = requests.get(clock_url, headers=headers)
    return json.loads(request.content)


def get_stock_data(ticker):
    parameters = {
    "apikey": td_key,
    "symbol": ticker
    }
    request = requests.get(url=td_quotes_url, params=parameters).json()
    data = pd.DataFrame.from_dict(request, orient='index').reset_index(drop=True)
    
    return data['lastPrice']


def make_df(ticker):
    
    vwap = indicators.get_vwap(symbol=ticker, interval='15min',)[0]
    data = time_series_data.get_intraday(symbol=ticker, interval='15min', outputsize='full')
    data = data[0].iloc[::-1]
    data[f'{ticker}pct_change'] = (data['4. close'] - data['1. open'])/ data['1. open'] * 100
    df = data.join(vwap)
    df[f'{ticker} price/vwap range'] = df['4. close'] - df['VWAP']
    df.to_csv(f"C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Data\\{ticker}.csv", index=True)
    global ranges
    ranges = [value for value in df[f'{ticker} price/vwap range'].values[-220:]]

    return(df[f'{ticker} price/vwap range'][-1], df['4. close'][-1])


def check_vwap(ticker):

    while get_clock()["is_open"] == True:

        new_data = make_df(ticker)
        new_range = new_data[0]
        largest_range = max(ranges)

        if new_range == largest_range:
            print('watch function triggered')
            trigger_buy()
            profit_loss()
        else:
            print('...')
            time.sleep(900.1)


def trigger_buy():

    while get_clock()["is_open"] == True:

        new_data = make_df(ticker)

        if (new_data[1] <=  new_data[0]*1.03) and [range > 0 for range in ranges[-3:]]:
            client.messages.create(
                to = '+4407860209951',
                from_= '+13343453192',
                body=f'\nBUY SIGNAL FOR {ticker} TRIGGERED AT ${new_data[1]}.'
            )
            print('buy function triggered')
            # row = owned_stocks_df.loc[owned_stocks_df['Stock'] == ticker]
            # row['Owned'] = 'True'
            global entry_price 
            entry_price = new_data[1]
            break
        else:
            print('-')
            time.sleep(900.1)


def profit_loss():

    while get_clock()['is_open'] == True:
        
        last_price = get_stock_data(ticker)

        if last_price <= entry_price*0.94:
            client.messages.create(
                to = '+4407860209951',
                from_= '+13343453192',
                body=f'\nSTOP LOSS FOR {ticker} TRIGGERED AT ${last_price}.'
            )
            # row = owned_stocks_df.loc[owned_stocks_df['Stock'] == ticker]
            # row['Owned'] = 'False'
        elif last_price >= entry_price*1.1:
            client.messages.create(
                to = '+4407860209951',
                from_= '+13343453192',
                body=f'\nPOSITION IN {ticker} AT 10% PROFIT. - PRICE({last_price})'
            )
        elif last_price >= entry_price*1.15:
            client.messages.create(
                to = '+4407860209951',
                from_= '+13343453192',
                body=f'\nSTOP LOSS TRIGGERED FOR {ticker} AT 15% PROFIT. - PRICE({last_price})'
            )        
            # row = owned_stocks_df.loc[owned_stocks_df['Stock'] == ticker]
            # row['Owned'] = 'False'
        else:
            time.sleep(20)


if __name__ == '__main__':

    ticker = ['KGC', 'F', 'GE']
    # owned_stocks_df = pd.read_csv('C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Code\\Research\\Owned_Stocks.csv')
    
    with multiprocessing.Pool() as pool:
        results = pool.starmap(check_vwap, product(ticker))
    print(results)


