from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.data_cache import get_prices
from backend.analysis import (
    calculate_returns,
    covariance_matrix,
    correlation_matrix,
    expected_annual_returns,
    annual_covariance_matrix,
    random_portfolios,
    optimize_max_sharpe,
    optimize_min_volatility,
    portfolio_return,
    portfolio_volatility,
    efficient_frontier
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

@app.get("/frontier")
def frontier():

    tickers = get_sp500_tickers()
    tickers = tickers[:10]

    prices = get_prices(tickers)
    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    portfolios = random_portfolios(exp_returns, cov, num_portfolios=3000)

    max_sharpe = max(portfolios, key=lambda x: x["sharpe"])
    min_volatility = min(portfolios, key=lambda x: x["volatility"])

    return {
        "assets": tickers,
        "portfolios": portfolios,
        "max_sharpe": max_sharpe,
        "min_volatility": min_volatility
    }

@app.get("/optimize")
def optimize():

    tickers = get_sp500_tickers()
    tickers = tickers[:10]

    prices = get_prices(tickers)
    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    max_sharpe_weights = optimize_max_sharpe(exp_returns, cov)
    min_vol_weights = optimize_min_volatility(exp_returns, cov)

    max_sharpe_return = portfolio_return(max_sharpe_weights, exp_returns)
    max_sharpe_vol = portfolio_volatility(max_sharpe_weights, cov)

    min_vol_return = portfolio_return(min_vol_weights, exp_returns)
    min_vol_vol = portfolio_volatility(min_vol_weights, cov)

    return {
        "assets": tickers,
        "max_sharpe": {
            "return": round(max_sharpe_return, 4),
            "volatility": round(max_sharpe_vol, 4),
            "weights": dict(zip(tickers, max_sharpe_weights.round(4)))
        },
        "min_volatility": {
            "return": round(min_vol_return, 4),
            "volatility": round(min_vol_vol, 4),
            "weights": dict(zip(tickers, min_vol_weights.round(4)))
        }
    }

@app.get("/efficient-frontier")
def efficient_frontier_endpoint():

    tickers = get_sp500_tickers()
    tickers = tickers[:10]

    prices = get_prices(tickers)
    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    frontier = efficient_frontier(exp_returns, cov, points=30)

    max_sharpe_weights = optimize_max_sharpe(exp_returns, cov)
    min_vol_weights = optimize_min_volatility(exp_returns, cov)

    return {
        "assets": tickers,
        "frontier": frontier,
        "max_sharpe": {
            "return": round(portfolio_return(max_sharpe_weights, exp_returns), 4),
            "volatility": round(portfolio_volatility(max_sharpe_weights, cov), 4),
            "weights": dict(zip(tickers, max_sharpe_weights.round(4)))
        },
        "min_volatility": {
            "return": round(portfolio_return(min_vol_weights, exp_returns), 4),
            "volatility": round(portfolio_volatility(min_vol_weights, cov), 4),
            "weights": dict(zip(tickers, min_vol_weights.round(4)))
        }
    }