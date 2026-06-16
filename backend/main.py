from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.data_cache import get_prices
from backend.assets import get_all_assets, get_sp500_tickers
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
    efficient_frontier,
    portfolio_backtest,
    filter_prices_by_period,
    backtest_metrics,
    single_asset_backtest
)

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


@app.get("/assets")
def assets():
    return {"assets": get_all_assets()}


@app.get("/analysis")
def analysis():
    tickers = get_sp500_tickers()[:10]

    prices = get_prices(tickers)
    returns = calculate_returns(prices)

    cov = covariance_matrix(returns)
    corr = correlation_matrix(returns)

    return {
        "number_of_assets": len(tickers),
        "assets": tickers,
        "number_of_observations": len(returns),
        "correlation_shape": corr.shape,
        "covariance_shape": cov.shape,
        "metrics": metrics
    }


@app.get("/correlation")
def correlation(
    tickers: str = "AAPL,MSFT,NVDA,BRK-B,LLY",
    period: str = "5y"
):
    ticker_list = tickers.split(",")[:10]

    prices = get_prices(ticker_list)
    prices = filter_prices_by_period(prices, period)

    returns = calculate_returns(prices)
    corr = correlation_matrix(returns)

    return {
        "assets": ticker_list,
        "correlation": corr.round(4).to_dict()
    }


@app.get("/frontier")
def frontier():
    tickers = get_sp500_tickers()[:10]

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
    tickers = get_sp500_tickers()[:10]

    prices = get_prices(tickers)
    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    max_sharpe_weights = optimize_max_sharpe(exp_returns, cov)
    min_vol_weights = optimize_min_volatility(exp_returns, cov)

    return {
        "assets": tickers,
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


@app.get("/efficient-frontier")
def efficient_frontier_endpoint(
    tickers: str = "AAPL,MSFT,NVDA,BRK-B,LLY",
    max_weight: float = 1.0,
    period: str = "5y"
):
    ticker_list = tickers.split(",")[:10]

    prices = get_prices(ticker_list)
    prices = filter_prices_by_period(prices, period)

    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    frontier = efficient_frontier(
        exp_returns,
        cov,
        points=30,
        max_weight=max_weight
    )

    max_sharpe_weights = optimize_max_sharpe(
        exp_returns,
        cov,
        max_weight=max_weight
    )

    min_vol_weights = optimize_min_volatility(
        exp_returns,
        cov,
        max_weight=max_weight
    )

    return {
        "assets": ticker_list,
        "frontier": frontier,
        "max_sharpe": {
            "return": round(portfolio_return(max_sharpe_weights, exp_returns), 4),
            "volatility": round(portfolio_volatility(max_sharpe_weights, cov), 4),
            "weights": dict(zip(ticker_list, max_sharpe_weights.round(4)))
        },
        "min_volatility": {
            "return": round(portfolio_return(min_vol_weights, exp_returns), 4),
            "volatility": round(portfolio_volatility(min_vol_weights, cov), 4),
            "weights": dict(zip(ticker_list, min_vol_weights.round(4)))
        }
    }


@app.get("/backtest")
def backtest(
    tickers: str = "AAPL,MSFT,BTC-USD,GLD,TLT",
    max_weight: float = 0.3,
    capital: float = 100000,
    period: str = "5y"
):
    ticker_list = tickers.split(",")[:10]

    prices = get_prices(ticker_list)
    prices = filter_prices_by_period(prices, period)

    returns = calculate_returns(prices)

    exp_returns = expected_annual_returns(returns)
    cov = annual_covariance_matrix(returns)

    weights = optimize_max_sharpe(
        exp_returns,
        cov,
        max_weight=max_weight
    )

    portfolio_value = portfolio_backtest(
        prices,
        weights,
        initial_capital=capital
    )

    metrics = backtest_metrics(portfolio_value)

    benchmark_tickers = {
        "sp500": "SPY",
        "bitcoin": "BTC-USD",
        "gold": "GLD",
        "treasury": "TLT"
    }

    benchmark_values = {}

    benchmark_prices = get_prices(list(benchmark_tickers.values()))
    benchmark_prices = filter_prices_by_period(benchmark_prices, period)

    for name, ticker in benchmark_tickers.items():
        if ticker in benchmark_prices.columns:
            benchmark_values[name] = single_asset_backtest(
                benchmark_prices[ticker],
                initial_capital=capital
            ).round(2).tolist()

    return {
        "assets": ticker_list,
        "weights": dict(zip(ticker_list, weights.round(4))),
        "dates": [str(date.date()) for date in portfolio_value.index],
        "values": portfolio_value.round(2).tolist(),
        "metrics": metrics,
        "benchmarks": benchmark_values
    }

