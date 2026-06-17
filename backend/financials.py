import yfinance as yf


def safe_round(value):
    if value is None:
        return None

    try:
        return round(value, 1)
    except Exception:
        return None


def get_financial_data(tickers):
    result = []

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info

            enterprise_value = info.get("enterpriseValue")
            ebitda = info.get("ebitda")
            ebit_ev = None

            if enterprise_value and ebitda:
                ebit_ev = safe_round(
                    ebitda / enterprise_value * 100
                )

            operating_cashflow = info.get("operatingCashflow")
            revenue = info.get("totalRevenue")
            ocf_margin = None

            if operating_cashflow and revenue:
                ocf_margin = safe_round(
                    operating_cashflow / revenue * 100
                )

            roc = None

            if info.get("returnOnAssets") is not None:
                roc = safe_round(
                    info.get("returnOnAssets") * 100
                )

            result.append({
                "ticker": ticker,

                "pe": safe_round(info.get("trailingPE")),
                "pb": safe_round(info.get("priceToBook")),
                "ps": safe_round(info.get("priceToSalesTrailing12Months")),

                "debt_to_equity": safe_round(
                    info.get("debtToEquity")
                ),

                "roe": safe_round(
                    info.get("returnOnEquity") * 100
                ) if info.get("returnOnEquity") is not None else None,

                "operating_margin": safe_round(
                    info.get("operatingMargins") * 100
                ) if info.get("operatingMargins") is not None else None,

                "ebitda_margin": safe_round(
                    info.get("ebitdaMargins") * 100
                ) if info.get("ebitdaMargins") is not None else None,

                "ebit_ev": ebit_ev,
                "ocf_margin": ocf_margin,
                "roc": roc
            })

        except Exception as e:
            result.append({
                "ticker": ticker,
                "error": str(e)
            })

    return result