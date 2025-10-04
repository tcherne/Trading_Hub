import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 0)           # No line wrapping
from openbb import obb
obb.user.preferences.output_type = "dataframe"
import pandas_datareader as pdr

# get historical price data
# data = obb.equity.price.historical("SPY", provider="yfinance")
# print(data)

# get historical fundamental data
# data = obb.equity.fundamental.metrics("AAPL", provider="yfinance")
# print(data)

# build a screener on industry valuation
# data = obb.equity.compare.groups(groups="industry", metric="valuation", provider="finviz")
# print(data)

# build a screener for top gainers from tech
# data = obb.equity.compare.groups(group="technology", metric="performance", provider="finviz")
# print(data)

# build screener for overview grouped by sector
# data = obb.equity.compare.groups(group="sector", metric="overview", provider="finviz")
# print(data) 

# futures curve data and plot
# data = obb.derivatives.futures.curve(symbol="VX")
# print(data)
# data.index = pd.to_datetime(data['expiration'])
# data.plot()
# plt.show()

# Get historical futures data for multiple expirations and combine into a single DataFrame
# expirations = [
#     '2026-12',
#     '2027-12',
#     '2028-12',
#     '2029-12',
#     '2030-12',
# ]
# contracts = []
# for expiration in expirations:
#     try:
#         df = (
#                 obb
#                 .derivatives
#                 .futures
#                 .historical(
#                     symbol="CL", 
#                     expiration=expiration, 
#                     start_date="2020-01-01", 
#                     end_date= "2022-12-31",
#                     provider="yfinance")                  
#                     ).rename(columns={
#                         "close":expiration
#                     })
#         contracts.append(df[expiration])
#     except Exception as e:
#         print(f"Error fetching data for {expiration}: {e}")
# historical = (pd.DataFrame(contracts).transpose().dropna())
# print(historical)
# historical.iloc[-1].plot()
# plt.show()

# options chains, get all symbols
# chains = obb.derivatives.options.chains("NNE")
# chains.info()
# print(chains.tail())

# option historical data for one symbol
# data = obb.equity.price.historical(symbol="NNE280121P00060000", provider="yfinance")[["close", "volume"]]
# print(data.head())

# Fama French factors
# factors = pdr.get_data_famafrench("F-F_Research_Data_Factors")
# print(factors["DESCR"])
# print(factors[0].tail())
# print(factors[1].tail())