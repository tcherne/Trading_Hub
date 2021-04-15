#!/usr/bin/env python
# coding: utf-8

# In[13]:


import requests, cloudscraper
import pandas as pd
import numpy as np
from io import StringIO


# In[14]:


def download_csv(url, csv_format):
    scraper = cloudscraper.create_scraper()
    with requests.get(url, stream=True) as r:
        text = StringIO(scraper.get(url).text)
        if csv_format == 'ark':
            clean_ark(text)
        if csv_format == 'globalx':
            clean_globalx(text)
        if csv_format == 'ishares':
            clean_ishares(text)


# In[15]:


def clean_ark(text):
    df = pd.read_csv(text)
    df.rename(columns = {'ticker':'ticker',
                         'company':'company',
                         'weight(%)':'weight',
                         'market value($)':'market_value',
                         'shares':'shares',
                        }, inplace = True)
    df.drop(['date', 'fund', 'cusip'], axis=1, inplace=True)
    df['price'] = df['market_value']/df['shares']
    df.set_index('ticker', inplace=True)
    df = df[['company', 'weight', 'market_value', 'shares']]
    display(df.head())


# In[16]:


def clean_globalx(text):
    df = pd.read_csv(text, header=2)
    df.rename(columns = {'Ticker':'ticker',
                     'Name':'company',
                     '% of Net Assets':'weight',
                     'Market Value ($)':'market_value',
                     'Shares Held':'shares',
                    }, inplace = True)
    df.drop(['SEDOL', 'Market Price ($)'], axis=1, inplace=True)
    df['market_value'] = pd.to_numeric(df['market_value'].str.replace(',',''))
    df['shares'] = pd.to_numeric(df['shares'].str.replace(',',''))
    df['price'] = df['market_value']/df['shares']
    df.set_index('ticker', inplace=True)
    df = df[['company', 'weight', 'market_value', 'shares']]
    display(df.head())


# In[17]:


def clean_ishares(text):
    df = pd.read_csv(text, header=9)
    df.rename(columns = {'Ticker':'ticker',
                 'Name':'company',
                 'Weight (%)':'weight',
                 'Market Value':'market_value',
                 'Shares':'shares',
                }, inplace = True)
    df.drop(['Sector', 'Asset Class', 'Notional Value', 'CUSIP', 'ISIN', 'SEDOL', 'Price', 'Location', 'Exchange', 'Currency', 'FX Rate', 'Market Currency', 'Accrual Date'], axis=1, inplace=True)
    df['market_value'] = pd.to_numeric(df['market_value'].str.replace(',',''))
    df['shares'] = pd.to_numeric(df['shares'].str.replace(',',''))
    df['price'] = df['market_value']/df['shares']
    df.set_index('ticker', inplace=True)    
    df = df[['company', 'weight', 'market_value', 'shares']]
    display(df.head())


# In[18]:


url_ark='https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv'
url_globalx='https://www.globalxetfs.com/funds/botz/?download_full_holdings=true'
url_ishares='https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund'

csv_format = 'ark'
download_csv(url_ark, csv_format)
csv_format = 'globalx'
download_csv(url_globalx, csv_format)
csv_format = 'ishares'
download_csv(url_ishares, csv_format)


# In[ ]:





# In[ ]:




