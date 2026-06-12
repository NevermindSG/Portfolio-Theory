#IDEE (Kernpipeline)
# &P500 Liste
 #      ↓
#Ticker auswählen
 #      ↓
#Kurse aus Cache laden
 #      ↓
#Returns berechnen
  #     ↓
#Risiko berechnen
 #      ↓
#Korrelation berechnen
 #      ↓
#JSON zurückgeben

from fastapi import FastAPI

from backend.data_cache import get_prices
from backend.analysis import (
    calculate_returns,
    covariance_matrix,
    correlation_matrix
)

from backend.assets import get_sp500_tickers


app = FastAPI()


@app.get("/")
def home():
    return {
        "status": "Portfolio Engine läuft"
    }


@app.get("/analysis")
def analysis():

    tickers = get_sp500_tickers()

    # erstmal nur 10 Titel zum Testen
    tickers = tickers[:10]

    prices = get_prices(tickers)

    returns = calculate_returns(prices)

    cov = covariance_matrix(returns)

    corr = correlation_matrix(returns)


    return {
        "assets": tickers,
        "covariance": cov.to_dict(),
        "correlation": corr.to_dict()
    }