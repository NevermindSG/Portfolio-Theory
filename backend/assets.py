import os
import pandas as pd


CSV_PATH = "data/sp500_assets.csv"


EXTRA_ASSETS = [
    {"ticker": "BTC-USD", "name": "Bitcoin", "asset_class": "Crypto", "sector": "Crypto"},
    {"ticker": "GLD", "name": "Gold ETF", "asset_class": "Commodity", "sector": "Gold"},
    {"ticker": "TLT", "name": "20+ Year Treasury ETF", "asset_class": "Bond", "sector": "Treasury"},
    {"ticker": "IEF", "name": "7-10 Year Treasury ETF", "asset_class": "Bond", "sector": "Treasury"},
    {"ticker": "SHY", "name": "1-3 Year Treasury ETF", "asset_class": "Bond", "sector": "Treasury"},
]


def load_sp500_assets():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV nicht gefunden: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    return df.to_dict(orient="records")


def get_all_assets():
    return load_sp500_assets() + EXTRA_ASSETS


def get_assets():
    return get_all_assets()


def get_sp500_tickers():
    assets = load_sp500_assets()
    return [asset["ticker"] for asset in assets]