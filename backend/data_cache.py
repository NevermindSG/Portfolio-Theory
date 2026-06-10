import yfinance as yf
import pandas as pd
import os

CACHE_DIR = "data_cache"

os.makedirs(CACHE_DIR, exist_ok=True)


def load_ticker(ticker):
    path = f"{CACHE_DIR}/{ticker}.csv"
    
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

    df = yf.download(ticker, period="5y")["Close"]
    df.to_csv(path)
    return df


def get_prices(tickers):
    data = {}

    for t in tickers:
        try:
            data[t] = load_ticker(t)
        except:
            pass

    return pd.DataFrame(data).dropna()