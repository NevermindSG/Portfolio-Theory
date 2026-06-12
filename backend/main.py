from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.data_cache import get_prices
from backend.analysis import (
    calculate_returns,
    covariance_matrix,
    correlation_matrix
)

from backend.assets import get_sp500_tickers

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "Portfolio Engine läuft"}


@app.get("/analysis")
def analysis():

    tickers = get_sp500_tickers()
    tickers = tickers[:10]

    prices = get_prices(tickers)

    returns = calculate_returns(prices)

    cov = covariance_matrix(returns)
    corr = correlation_matrix(returns)

    return {
        "number_of_assets": len(tickers),
        "assets": tickers,
        "number_of_observations": len(returns),
        "correlation_shape": corr.shape,
        "covariance_shape": cov.shape
    }


@app.get("/correlation")
def correlation():

    tickers = get_sp500_tickers()
    tickers = tickers[:10]

    prices = get_prices(tickers)

    returns = calculate_returns(prices)

    corr = correlation_matrix(returns)

    return {
        "assets": tickers,
        "correlation": corr.round(4).to_dict()
    }