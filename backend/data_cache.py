import os
import pandas as pd
import yfinance as yf


CACHE_DIR = "data_cache"


def load_ticker(ticker):
    file_path = os.path.join(CACHE_DIR, f"{ticker}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)

        if "Close" in df.columns:
            series = df["Close"].copy()
            series.name = ticker
            return series

        if ticker in df.columns:
            series = df[ticker].copy()
            series.name = ticker
            return series

        if len(df.columns) == 1:
            series = df.iloc[:, 0].copy()
            series.name = ticker
            return series

        raise ValueError(f"Keine passende Kursspalte für {ticker}")

    data = yf.download(
        ticker,
        period="10y",
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        raise ValueError(f"Keine Daten für {ticker}")

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    close = data["Close"].copy()
    close.name = ticker

    os.makedirs(CACHE_DIR, exist_ok=True)

    close.to_frame("Close").to_csv(file_path)

    return close


def get_prices(tickers):
    series_list = []

    for ticker in tickers:
        try:
            series = load_ticker(ticker)
            series_list.append(series)

        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")

    if not series_list:
        raise ValueError("Keine Kursdaten geladen")

    prices = pd.concat(series_list, axis=1)
    prices = prices.dropna()

    return prices