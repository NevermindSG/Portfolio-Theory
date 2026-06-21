from backend.financials import get_financial_data
from backend.scoring import calculate_scores
from backend.sector_averages import load_sector_map


def passes_filter(value, min_value=None, max_value=None, absolute=False):
    if value is None:
        return False

    test_value = abs(value) if absolute else value

    if min_value is not None and test_value < min_value:
        return False

    if max_value is not None and test_value > max_value:
        return False

    return True


def run_screener(
    tickers,
    max_200d=None,
    max_200w=None,
    max_pe=None,
    min_roe=None,
    min_quality=None,
    min_value=None,
    min_total=None,
    sector=None
):
    financials = get_financial_data(tickers)
    scores = calculate_scores(financials)
    sector_map = load_sector_map()

    score_lookup = {
        item["ticker"]: item
        for item in scores
    }

    results = []

    for financial in financials:
        ticker = financial.get("ticker")
        score = score_lookup.get(ticker)

        if not score:
            continue

        if max_pe is not None and not passes_filter(financial.get("pe"), max_value=max_pe):
            continue

        if min_roe is not None and not passes_filter(financial.get("roe"), min_value=min_roe):
            continue

        if max_200d is not None and not passes_filter(score.get("distance_200d"), max_value=max_200d, absolute=True):
            continue

        if max_200w is not None and not passes_filter(score.get("distance_200w"), max_value=max_200w, absolute=True):
            continue

        if min_quality is not None and not passes_filter(score.get("quality_score"), min_value=min_quality):
            continue

        if min_value is not None and not passes_filter(score.get("value_score"), min_value=min_value):
            continue

        if min_total is not None and not passes_filter(score.get("total_score"), min_value=min_total):
            continue
        if sector is not None and sector_map.get(ticker) != sector:
            continue

        results.append({
            "ticker": ticker,
            "pe": financial.get("pe"),
            "roe": financial.get("roe"),
            "distance_200d": score.get("distance_200d"),
            "distance_200w": score.get("distance_200w"),
            "value_score": score.get("value_score"),
            "quality_score": score.get("quality_score"),
            "trend_score": score.get("trend_score"),
            "total_score": score.get("total_score")
        })

    results = sorted(
        results,
        key=lambda x: x["total_score"] if x["total_score"] is not None else -1,
        reverse=True
    )

    return results