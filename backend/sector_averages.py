import pandas as pd

from backend.financials import get_financial_data


ASSETS_CSV = "data/sp500_assets.csv"


def safe_average(values):
    clean_values = [
        value for value in values
        if value is not None
    ]

    if len(clean_values) == 0:
        return None

    return round(sum(clean_values) / len(clean_values), 1)


def load_sector_map():
    df = pd.read_csv(ASSETS_CSV)

    return {
        row["ticker"]: row["sector"]
        for _, row in df.iterrows()
        if "ticker" in row and "sector" in row
    }


def calculate_sector_averages(tickers):
    sector_map = load_sector_map()
    financials = get_financial_data(tickers)

    grouped = {}

    for item in financials:
        ticker = item.get("ticker")
        sector = sector_map.get(ticker)

        if sector is None:
            continue

        if sector not in grouped:
            grouped[sector] = []

        grouped[sector].append(item)

    results = []

    for sector, items in grouped.items():
        results.append({
            "sector": sector,
            "count": len(items),
            "pe": safe_average([item.get("pe") for item in items]),
            "pb": safe_average([item.get("pb") for item in items]),
            "ps": safe_average([item.get("ps") for item in items]),
            "debt_to_equity": safe_average([item.get("debt_to_equity") for item in items]),
            "roe": safe_average([item.get("roe") for item in items]),
            "operating_margin": safe_average([item.get("operating_margin") for item in items]),
            "ebitda_margin": safe_average([item.get("ebitda_margin") for item in items]),
            "roc": safe_average([item.get("roc") for item in items]),
            "ebit_ev": safe_average([item.get("ebit_ev") for item in items]),
            "ocf_margin": safe_average([item.get("ocf_margin") for item in items])
        })

    results = sorted(
        results,
        key=lambda x: x["sector"]
    )

    return results