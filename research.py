import pandas as pd
from config import *
from alpha_vantage.timeseries import TimeSeries

time_series_data = TimeSeries(alphavantage_key, output_format='pandas')

data = pd.read_csv(f"C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Code\\Research\\KGC.csv").set_index('date')
GLD = time_series_data.get_intraday(symbol='GLD', interval='15min', outputsize='compact')
GLD = GLD[0].iloc[::-1]
GLD['GLD pct_change'] = (GLD['4. close'] - GLD['1. open'])/ GLD['1. open'] * 100
df = data.join(GLD['GLD pct_change'])
df.drop(['1. open', '2. high', '3. low', '4. close'], axis=1, inplace=True)
# df  = pd.read_csv("C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Code\\Research\\KGC.csv")
df['five period forward change'] = df['pct_change'].rolling(190).sum().shift(-2)
df['3 period cumulative change'] = df['pct_change'].rolling(48).sum()
df['GLD 3 period cumulative change'] = df['GLD pct_change'].rolling(48).sum()
# df['KGC - GLD 3 period return'] = df['3 period cumulative change'] - df['GLD 3 period cumulative change']
# df['performace/vwap'] = df['KGC - GLD 3 period return'] / abs(df['price/vwap range'])
# df = df[['price/vwap range', 'KGC - GLD 3 period return', 'five period forward change', 'performace/vwap']]
print(df.tail(30))

