import yfinance as yf
import pandas as pd
import numpy as np
# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from hmmlearn import hmm

# Define the tickers
tickers = {
    'stock': 'AAPL',  # Example stock
    'sector': 'XLK',  # Technology sector ETF
    'market': '^GSPC'  # S&P 500 index
}

# Fetch historical data
data = {}
for key, ticker in tickers.items():
    try:
        df = yf.download(ticker, start="2020-01-01", end="2025-01-01")
        # Use 'Adj Close' if available, otherwise use 'Close'
        if 'Adj Close' in df.columns:
            # Extract the 'Adj Close' column as a pandas Series
            data[key] = df['Adj Close'].squeeze()
        else:
            # Extract the 'Close' column as a pandas Series
            data[key] = df['Close'].squeeze()
        print(f"Data for {ticker} fetched successfully.")
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")

# Check if data is empty
if not data:
    raise ValueError("No data fetched. Check the tickers and try again.")

# Calculate daily returns
returns = {}
for key, series in data.items():
    if not series.empty:
        # Ensure the series is a pandas Series
        if isinstance(series, pd.Series):
            returns[key] = series.pct_change().dropna()
            print(f"Returns for {key} calculated successfully.")
        else:
            print(f"Data for {key} is not a pandas Series.")
    else:
        print(f"No data available for {key}.")

# Check if returns are empty
if not returns:
    raise ValueError("No returns calculated. Check the data and try again.")

# Print the structure of returns
print("Structure of returns dictionary:")
for key, value in returns.items():
    print(f"{key}: {type(value)}")

# Ensure all Series in returns have the same index
common_index = returns[list(returns.keys())[0]].index
for key, series in returns.items():
    if not series.index.equals(common_index):
        print(f"Index mismatch for {key}. Aligning indices.")
        returns[key] = series.reindex(common_index).dropna()

# Combine returns into a single DataFrame
returns_df = pd.DataFrame(returns)

# Check if the DataFrame is empty
if returns_df.empty:
    raise ValueError("Returns DataFrame is empty. Check the data and try again.")

# Print the first few rows of the DataFrame
print("First few rows of returns DataFrame:")
print(returns_df.head())

# Prepare the data for HMM
X = returns_df.values

# Define the HMM model
model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=1000)

# Fit the model
model.fit(X)

# Predict the hidden states
hidden_states = model.predict(X)

# Add hidden states to the DataFrame
returns_df['HiddenState'] = hidden_states

# Plot the results
plt.figure(figsize=(14, 8))
for i in range(model.n_components):
    state = (returns_df['HiddenState'] == i)
    plt.plot(returns_df.index[state], returns_df['market'][state], '.', label=f'State {i}')
plt.legend()
plt.title('Market Regimes Classified by HMM')
plt.xlabel('Date')
plt.ylabel('Market Returns')
plt.show()

# Calculate mean and variance for each state
state_means = []
state_variances = []
for i in range(model.n_components):
    state_means.append(returns_df[returns_df['HiddenState'] == i]['market'].mean())
    state_variances.append(returns_df[returns_df['HiddenState'] == i]['market'].var())

# Print the results
for i in range(model.n_components):
    print(f"State {i} - Mean: {state_means[i]}, Variance: {state_variances[i]}")