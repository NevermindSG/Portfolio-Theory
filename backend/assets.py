ASSETS = [
    {"ticker": "AAPL", "name": "Apple", "asset_class": "Stock"},
    {"ticker": "MSFT", "name": "Microsoft", "asset_class": "Stock"},
    {"ticker": "NVDA", "name": "Nvidia", "asset_class": "Stock"},
    {"ticker": "AMZN", "name": "Amazon", "asset_class": "Stock"},
    {"ticker": "META", "name": "Meta", "asset_class": "Stock"},
    {"ticker": "GOOGL", "name": "Alphabet A", "asset_class": "Stock"},
    {"ticker": "BRK-B", "name": "Berkshire Hathaway", "asset_class": "Stock"},
    {"ticker": "LLY", "name": "Eli Lilly", "asset_class": "Stock"},
    {"ticker": "AVGO", "name": "Broadcom", "asset_class": "Stock"},

    {"ticker": "BTC-USD", "name": "Bitcoin", "asset_class": "Crypto"},
    {"ticker": "GLD", "name": "Gold ETF", "asset_class": "Commodity"},
    {"ticker": "TLT", "name": "20+ Year Treasury ETF", "asset_class": "Bond"},
    {"ticker": "IEF", "name": "7-10 Year Treasury ETF", "asset_class": "Bond"},
    {"ticker": "SHY", "name": "1-3 Year Treasury ETF", "asset_class": "Bond"},
]


def get_assets():
    return ASSETS


def get_sp500_tickers():
    return [asset["ticker"] for asset in ASSETS]