import os
import pandas as pd

URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
OUTPUT_PATH = "data/sp500_assets.csv"

os.makedirs("data", exist_ok=True)

df = pd.read_csv(URL)

assets = df[["Symbol", "Security", "GICS Sector"]].copy()

assets.columns = [
    "ticker",
    "name",
    "sector"
]

assets["ticker"] = assets["ticker"].str.replace(".", "-", regex=False)
assets["asset_class"] = "Stock"

assets = assets[
    [
        "ticker",
        "name",
        "asset_class",
        "sector"
    ]
]

assets.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8"
)

print(f"S&P500 Liste gespeichert: {OUTPUT_PATH}")
print(f"Anzahl Assets: {len(assets)}")
print(assets.head())