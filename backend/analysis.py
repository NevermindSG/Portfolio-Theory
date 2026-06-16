import numpy as np
import pandas as pd
from scipy.optimize import minimize


def calculate_returns(price_df):
    return price_df.pct_change().dropna()


def covariance_matrix(returns_df):
    return returns_df.cov()


def correlation_matrix(returns_df):
    return returns_df.corr()


def expected_annual_returns(returns_df):
    return returns_df.mean() * 252


def annual_covariance_matrix(returns_df):
    return returns_df.cov() * 252


def portfolio_return(weights, expected_returns):
    return float(np.dot(weights, expected_returns))


def portfolio_volatility(weights, cov_matrix):
    return float(np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))))


def random_portfolios(expected_returns, cov_matrix, num_portfolios=5000):
    results = []

    assets = expected_returns.index.tolist()
    num_assets = len(assets)

    for _ in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights = weights / np.sum(weights)

        ret = portfolio_return(weights, expected_returns)
        vol = portfolio_volatility(weights, cov_matrix)
        sharpe = ret / vol if vol != 0 else 0

        results.append({
            "return": ret,
            "volatility": vol,
            "sharpe": sharpe,
            "weights": dict(zip(assets, weights.round(4)))
        })

    return results

def negative_sharpe_ratio(weights, expected_returns, cov_matrix, risk_free_rate=0.0):
    ret = portfolio_return(weights, expected_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    return -((ret - risk_free_rate) / vol)


def optimize_max_sharpe(expected_returns, cov_matrix, risk_free_rate=0.0, max_weight=1.0):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, max_weight) for _ in range(num_assets))
    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1},
    )

    result = minimize(
        negative_sharpe_ratio,
        initial_weights,
        args=(expected_returns, cov_matrix, risk_free_rate),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    return result.x

    result = minimize(
        negative_sharpe_ratio,
        initial_weights,
        args=(expected_returns, cov_matrix, risk_free_rate),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    return result.x

def optimize_min_volatility(expected_returns, cov_matrix, max_weight=1.0):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, max_weight) for _ in range(num_assets))
    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1},
    )

    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    return result.x



    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    return result.x

def minimize_volatility_for_target_return(target_return, expected_returns, cov_matrix, max_weight=1.0):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, max_weight) for _ in range(num_assets))

    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1},
        {"type": "eq", "fun": lambda weights: portfolio_return(weights, expected_returns) - target_return},
    )

    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        return None

    return result.x

    result = minimize(
        portfolio_volatility,
        initial_weights,
        args=(cov_matrix,),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:
        return None

    return result.x


def efficient_frontier(expected_returns, cov_matrix, points=30, max_weight=1.0):
    min_return = expected_returns.min()
    max_return = expected_returns.max()

    target_returns = np.linspace(min_return, max_return, points)

    frontier = []

    for target in target_returns:
        weights = minimize_volatility_for_target_return(
            target,
            expected_returns,
            cov_matrix,
            max_weight=max_weight
        )

        if weights is None:
            continue

        ret = portfolio_return(weights, expected_returns)
        vol = portfolio_volatility(weights, cov_matrix)

        frontier.append({
            "return": round(ret, 4),
            "volatility": round(vol, 4),
            "weights": dict(zip(expected_returns.index.tolist(), weights.round(4)))
        })

    return frontier

def portfolio_backtest(price_df, weights, initial_capital=100000):
        returns = calculate_returns(price_df)

        portfolio_returns = returns.dot(weights)

        portfolio_value = (1 + portfolio_returns).cumprod() * initial_capital

        return portfolio_value

def filter_prices_by_period(price_df, period="5y"):
    end_date = price_df.index.max()

    if period == "6mo":
        start_date = end_date - pd.DateOffset(months=6)
    elif period == "1y":
        start_date = end_date - pd.DateOffset(years=1)
    elif period == "3y":
        start_date = end_date - pd.DateOffset(years=3)
    else:
        start_date = end_date - pd.DateOffset(years=5)

    return price_df[price_df.index >= start_date]

def backtest_metrics(portfolio_value):
    start_value = portfolio_value.iloc[0]
    end_value = portfolio_value.iloc[-1]

    total_return = (end_value / start_value) - 1

    days = (portfolio_value.index[-1] - portfolio_value.index[0]).days
    years = days / 365.25

    cagr = (end_value / start_value) ** (1 / years) - 1

    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value / running_max) - 1
    max_drawdown = drawdown.min()

    return {
        "start_value": round(start_value, 2),
        "end_value": round(end_value, 2),
        "total_return": round(total_return, 4),
        "cagr": round(cagr, 4),
        "max_drawdown": round(max_drawdown, 4)
    }

def single_asset_backtest(price_series, initial_capital=100000):
    normalized = price_series / price_series.iloc[0]
    value = normalized * initial_capital

    return value