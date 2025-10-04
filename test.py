import requests
import certifi

url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&outputsize=full&apikey=G6YCFAOQQ1XEYOAU&datatype=json"
try:
    response = requests.get(url, verify=certifi.where())
    response.raise_for_status()
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")