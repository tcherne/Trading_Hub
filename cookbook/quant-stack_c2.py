import numpy as np
import pandas as pd
from openbb import obb
obb.user.preferences.output_type = "dataframe"

pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 0)           # No line wrapping


# Reindex an exisigting df with a multiindex
# chains = obb.derivatives.options.chains("SPY", providers="cboe")
# print(chains.head())

# df_3 = chains.set_index(['expiration', 'strike', 'option_type'])
# print(df_3.head())
# print(df_3.index)

# # common df functions
# asset = obb.equity.price.historical("AAPL", provider="yfinance")
# benchmark = obb.equity.price.historical("SPY", provider="yfinance")
# print(asset.head())
# columns= ["open", "high", "low", "close", "volume", "dividends"]
# asset.columns = columns
# # benchmark.columns = columns + ["capital_gain"]
# asset["price_diff"] = asset["close"].diff()
# benchmark["price_diff"] = benchmark["close"].diff()
# asset["gain"] = asset["price_diff"] > 0
# benchmark["gain"] = benchmark["price_diff"] > 0
# asset["symbol"] = "AAPL"
# benchmark["symbol"] = "SPY"
# print(asset.head())

# # pivot a table use this for economice release project
# print("Pivot Table")
# df_pivot = pd.pivot_table(data=asset, values="price_diff", columns="gain", aggfunc=["sum", "mean", "std"])
# print(df_pivot)

# # grouping data on a key or index and applying an aggregate
# print("Groupby")
# concated = pd.concat([asset, benchmark])
# df_con = concated.groupby("symbol").close.ohlc()
# print(df_con)

# Options Data and Straddles
chains = obb.derivatives.options.chains("AAPL", provider="cboe")

expirations = chains.expiration.unique()
calls = chains[(chains.option_type == "call") & (chains.expiration == expirations[5])]
puts = chains[(chains.option_type == "put") & (chains.expiration == expirations[5])]

calls_strike = calls.set_index("strike")
puts_strike = puts.set_index("strike")
joined = calls_strike.join(puts_strike, how="left", lsuffix="_call", rsuffix="_put")

prices = joined[["last_trade_price_call", "last_trade_price_put"]]
prices["straddle_price"] = prices.sum(axis=1)
print(prices)