from backend.momentum import (
    calculate_momentum_data,
    calculate_momentum_scores
)


def percentile_score(values, value, higher_is_better=True):
    clean_values = [
        v for v in values
        if v is not None
    ]

    if value is None or len(clean_values) == 0:
        return None

    better_count = 0

    for v in clean_values:
        if higher_is_better:
            if v <= value:
                better_count += 1
        else:
            if v >= value:
                better_count += 1

    score = better_count / len(clean_values) * 100

    return round(score, 1)


def calculate_scores(financials):
    tickers = [
        item["ticker"]
        for item in financials
    ]

    momentum_data = calculate_momentum_data(tickers)
    momentum_scores = calculate_momentum_scores(momentum_data)

    trend_lookup = {
    item["ticker"]: item
    for item in momentum_scores
}

    pe_values = [item.get("pe") for item in financials]
    pb_values = [item.get("pb") for item in financials]
    ps_values = [item.get("ps") for item in financials]
    ebit_ev_values = [item.get("ebit_ev") for item in financials]

    roe_values = [item.get("roe") for item in financials]
    roc_values = [item.get("roc") for item in financials]
    ocf_margin_values = [item.get("ocf_margin") for item in financials]
    operating_margin_values = [item.get("operating_margin") for item in financials]
    debt_to_equity_values = [item.get("debt_to_equity") for item in financials]

    scored = []

    for item in financials:
        value_components = [
            percentile_score(pe_values, item.get("pe"), higher_is_better=False),
            percentile_score(pb_values, item.get("pb"), higher_is_better=False),
            percentile_score(ps_values, item.get("ps"), higher_is_better=False),
            percentile_score(ebit_ev_values, item.get("ebit_ev"), higher_is_better=True),
        ]

        quality_components = [
            percentile_score(roe_values, item.get("roe"), higher_is_better=True),
            percentile_score(roc_values, item.get("roc"), higher_is_better=True),
            percentile_score(ocf_margin_values, item.get("ocf_margin"), higher_is_better=True),
            percentile_score(operating_margin_values, item.get("operating_margin"), higher_is_better=True),
            percentile_score(debt_to_equity_values, item.get("debt_to_equity"), higher_is_better=False),
        ]

        value_components = [
            x for x in value_components
            if x is not None
        ]

        quality_components = [
            x for x in quality_components
            if x is not None
        ]

        value_score = (
            round(sum(value_components) / len(value_components), 1)
            if value_components else None
        )

        quality_score = (
            round(sum(quality_components) / len(quality_components), 1)
            if quality_components else None
        )

        trend_data = trend_lookup.get(item["ticker"], {})

        trend_score = trend_data.get("trend_score")
        distance_200d = trend_data.get("distance_200d")
        distance_200w = trend_data.get("distance_200w")
        

        if (
            value_score is not None
            and quality_score is not None
            and trend_score is not None
        ):
            total_score = round(
                quality_score * 0.4 +
                value_score * 0.3 +
                trend_score * 0.3,
                1
            )
        else:
            total_score = None

        scored.append({
        "ticker": item["ticker"],
        "value_score": value_score,
        "quality_score": quality_score,
        "distance_200d": distance_200d,
        "distance_200w": distance_200w,
        "trend_score": trend_score,
        "total_score": total_score
    })

    scored = sorted(
        scored,
        key=lambda x: x["total_score"] if x["total_score"] is not None else -1,
        reverse=True
    )

    return scored