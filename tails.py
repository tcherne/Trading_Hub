import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import requests
import ssl
import certifi

# Print certifi path for debugging
print(certifi.where())

# Step 1: Configuration
ALPHA_VANTAGE_API_KEY = 'G6YCFAOQQ1XEYOAU'
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NFLX', 'NVDA']
# stocks = ['ACHR', 'ASTS', 'CRSP', 'DE', 'ELSE', 'MULN', 'NNE', 'NVDA', 'PLTR', 'QBTS', 'RDW', 'RKLB', 'SCWO', 'SPAI', 'TSLA', 'VOO']


start_date = '2025-01-01'
end_date = '2025-05-14'

# Create a requests session with certifi
session = requests.Session()
session.verify = certifi.where()  # Explicitly use certifi's CA bundle

# Step 2: Download data with retry mechanism
max_retries = 2
retry_delay = 15  # Seconds (Alpha Vantage: 5 calls/min = 12s/call)
data_frames = []

for stock in stocks:
    for attempt in range(max_retries):
        try:
            # Fetch daily data via direct API call
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}&datatype=json"
            response = session.get(url)
            response.raise_for_status()  # Raise exception for bad status codes
            # Parse JSON response
            data = pd.DataFrame(response.json()['Time Series (Daily)']).T
            # Rename '4. close' to 'Close'
            data = data.rename(columns={'4. close': 'Close'})
            # Convert index to datetime
            data.index = pd.to_datetime(data.index)
            # Sort index to ensure monotonicity
            data = data.sort_index()
            # Debugging: Print available date range
            print(f"Date range for {stock}: {data.index.min()} to {data.index.max()}")
            # Filter date range, clipping to available dates
            start = max(pd.to_datetime(start_date), data.index.min())
            end = min(pd.to_datetime(end_date), data.index.max())
            data = data.loc[start:end][['Close']].astype(float)
            data_frames.append(data.rename(columns={'Close': stock}))
            print(f"Downloaded data for {stock}")
            break
        except (ValueError, requests.exceptions.RequestException, KeyError, Exception) as e:
            print(f"Attempt {attempt + 1} failed for {stock}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print(f"Failed to download data for {stock} after {max_retries} attempts")
                data_frames.append(pd.DataFrame())  # Empty DataFrame for failed stock
        # Respect rate limit: 5 calls per minute
        time.sleep(12)

# Combine data into a single DataFrame
data = pd.concat(data_frames, axis=1)

# Step 3: Check if data is empty
if data.empty or data.isna().all().all():
    raise ValueError("No data downloaded. Check API key, tickers, or rate limits.")

# Step 4: Calculate daily returns
returns = data.pct_change().dropna()

# Step 5: Calculate tail ratio for each stock
def calculate_tail_ratio(returns_series, upper_percentile=0.95, lower_percentile=0.05):
    right_tail = np.percentile(returns_series, upper_percentile * 100)
    left_tail = np.percentile(returns_series, lower_percentile * 100)
    if left_tail == 0:
        return np.nan
    tail_ratio = abs(right_tail) / abs(left_tail)
    return tail_ratio

tail_ratios = {}
for stock in returns.columns:
    try:
        tail_ratios[stock] = calculate_tail_ratio(returns[stock])
    except Exception as e:
        print(f"Error calculating tail ratio for {stock}: {e}")
        tail_ratios[stock] = np.nan

# Step 6: Create DataFrame and filter stocks
tail_ratio_df = pd.DataFrame.from_dict(tail_ratios, orient='index', columns=['Tail Ratio'])
print("Tail Ratios for Stocks:")
print(tail_ratio_df)

threshold = 1.5
selected_stocks = tail_ratio_df[tail_ratio_df['Tail Ratio'] > threshold]
print("\nSelected Stocks (Tail Ratio > {}):".format(threshold))
print(selected_stocks)

# Step 7: Plot returns distribution
for stock in selected_stocks.index:
    plt.figure()
    returns[stock].hist(bins=50, alpha=0.5, label=stock)
    plt.title(f'Returns Distribution for {stock}')
    plt.xlabel('Daily Returns')
    plt.ylabel('Frequency')
    plt.legend()
    plt.show()