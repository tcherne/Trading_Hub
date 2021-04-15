#!/usr/bin/env python
# coding: utf-8

# In[7]:


import requests, cloudscraper
import pandas as pd
import numpy as np
from io import StringIO


# In[8]:


def download_csv(urls, csv_format):
    for url in urls:
        scraper = cloudscraper.create_scraper()
        with requests.get(url, stream=True) as r:
            text = StringIO(scraper.get(url).text)
            if csv_format == 'ark':
                clean_ark(text)
            if csv_format == 'globalx':
                clean_globalx(text)
            if csv_format == 'ishares':
                clean_ishares(text)


# In[9]:


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


# In[10]:


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


# In[11]:


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


# In[12]:


urls_ark = ['https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_GENOMIC_REVOLUTION_MULTISECTOR_ETF_ARKG_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_SPACE_EXPLORATION_&_INNOVATION_ETF_ARKX_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/THE_3D_PRINTING_ETF_PRNT_HOLDINGS.csv',
'https://ark-funds.com/wp-content/fundsiteliterature/csv/ARK_ISRAEL_INNOVATIVE_TECHNOLOGY_ETF_IZRL_HOLDINGS.csv']

urls_globalx = ['https://www.globalxetfs.com/funds/lit/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/pave/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/botz/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/qyld/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/pffd/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/clou/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/finx/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/sil/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/sdiv/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/driv/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/bug/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/mlpa/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/edoc/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/copx/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/mlpx/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/hero/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chiq/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/div/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/ura/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/cath/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/sret/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/socl/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/krma/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/snsr/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/ebiz/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/spff/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/gnom/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/xyld/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/aiq/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/miln/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/potx/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/ausf/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/ctec/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/grek/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/rnrg/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/ryld/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/embd/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/gxtg/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/guru/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/onof/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chix/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/goex/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/norw/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/gxg/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/argt/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/agng/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/nge/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chik/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/dax/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/sdem/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/gxf/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/pak/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/vpn/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/asea/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/bfit/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/alty/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chih/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/emfm/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chic/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/pffv/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/pgal/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/edut/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/boss/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/efas/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/qylg/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chil/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/qdiv/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/eweb/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chb/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/tfiv/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chir/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chim/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/tflt/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/keji/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/cefa/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/xylg/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chie/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chii/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/chiu/?download_full_holdings=true',
'https://www.globalxetfs.com/funds/aqwa/?download_full_holdings=true']

# csv_format = 'ark'
# download_csv(urls_ark, csv_format)
csv_format = 'globalx'
download_csv(urls_globalx, csv_format)
# csv_format = 'ishares'
# download_csv(url_ishares, csv_format)


# In[ ]:





# In[ ]:




