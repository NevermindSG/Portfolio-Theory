from backend.data_cache import get_prices


def proximity_score(value):
    if value is None:
        return None

    distance = abs(value)

    score = 100 - distance

    if score < 0:
        score = 0

    return round(score, 1)


def calculate_momentum_data(tickers):
    prices = get_prices(tickers)

    result = []

    for ticker in tickers:
        try:
            series = prices[ticker].dropna()

            if len(series) < 200:
                result.append({
                    "ticker": ticker,
                    "distance_200d": None,
                    "distance_200w": None
                })
                continue

            latest_price = series.iloc[-1]

            ma_200d = series.rolling(200).mean().iloc[-1]

            distance_200d = None
            if ma_200d is not None:
                distance_200d = (latest_price / ma_200d - 1) * 100

            distance_200w = None

            if len(series) >= 1000:
                ma_200w = series.rolling(1000).mean().iloc[-1]
                distance_200w = (latest_price / ma_200w - 1) * 100

            result.append({
                "ticker": ticker,
                "distance_200d": round(distance_200d, 1) if distance_200d is not None else None,
                "distance_200w": round(distance_200w, 1) if distance_200w is not None else None
            })

        except Exception as e:
            result.append({
                "ticker": ticker,
                "error": str(e)
            })

    return result


def calculate_momentum_scores(momentum_data):
    scored = []

    for item in momentum_data:
        score_200d = proximity_score(item.get("distance_200d"))
        score_200w = proximity_score(item.get("distance_200w"))

        components = [
            score for score in [score_200d, score_200w]
            if score is not None
        ]

        trend_score = (
            round(sum(components) / len(components), 1)
            if components else None
        )

        scored.append({
            "ticker": item.get("ticker"),
            "distance_200d": item.get("distance_200d"),
            "distance_200w": item.get("distance_200w"),
            "trend_score": trend_score
        })

    return sorted(
        scored,
        key=lambda x: x["trend_score"] if x["trend_score"] is not None else -1,
        reverse=True
    )