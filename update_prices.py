import os
import time
import pandas as pd
import yfinance as yf

ASSETS_CSV = "data/sp500_assets.csv"
CACHE_DIR = "data_cache"

EXTRA_TICKERS = [
    "BTC-USD",
    "GLD",
    "TLT",
    "SPY"
]


def load_tickers():
    tickers = []

    if os.path.exists(ASSETS_CSV):
        df = pd.read_csv(ASSETS_CSV)

        if "ticker" in df.columns:
            tickers = df["ticker"].dropna().tolist()

    tickers = tickers + EXTRA_TICKERS

    tickers = list(dict.fromkeys(tickers))

    return tickers


def update_ticker(ticker):
    print(f"Aktualisiere {ticker}...")

    data = yf.download(
        ticker,
        period="10y",
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        print(f"Keine Daten für {ticker}")
        return

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if "Close" not in data.columns:
        print(f"Keine Close-Spalte für {ticker}")
        return

    close = data[["Close"]].copy()
    close = close.dropna()

    file_path = os.path.join(CACHE_DIR, f"{ticker}.csv")
    close.to_csv(file_path)

    print(f"Gespeichert: {file_path}")


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)

    tickers = load_tickers()

    print(f"Starte Kursdaten-Update für {len(tickers)} Assets...")

    for ticker in tickers:
        try:
            update_ticker(ticker)
            time.sleep(0.2)

        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")

    print("Update abgeschlossen.")


if __name__ == "__main__":
    main()