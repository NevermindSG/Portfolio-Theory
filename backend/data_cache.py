import yfinance as yf
import pandas as pd
import os

CACHE_DIR = "data_cache"

os.makedirs(CACHE_DIR, exist_ok=True)


def load_ticker(ticker):
    path = f"{CACHE_DIR}/{ticker}.csv"

    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df[ticker]

    df = yf.download(
        ticker,
        period="5y",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise ValueError(f"Keine Daten für {ticker}")

    close = df["Close"]
    close.name = ticker

    close.to_csv(path, header=True)

    return close


def get_prices(tickers):
    series_list = []

    for ticker in tickers:
        try:
            s = load_ticker(ticker)
            series_list.append(s)
        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")

    if not series_list:
        raise ValueError("Keine Kursdaten geladen")

    prices = pd.concat(series_list, axis=1)
    return prices.dropna()