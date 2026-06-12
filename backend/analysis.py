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


def optimize_max_sharpe(expected_returns, cov_matrix, risk_free_rate=0.0):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}
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


def optimize_min_volatility(expected_returns, cov_matrix):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}
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

def minimize_volatility_for_target_return(target_return, expected_returns, cov_matrix):
    num_assets = len(expected_returns)
    initial_weights = np.array([1 / num_assets] * num_assets)

    bounds = tuple((0, 1) for _ in range(num_assets))

    constraints = (
        {"type": "eq", "fun": lambda weights: np.sum(weights) - 1},
        {"type": "eq", "fun": lambda weights: portfolio_return(weights, expected_returns) - target_return}
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


def efficient_frontier(expected_returns, cov_matrix, points=30):
    min_return = expected_returns.min()
    max_return = expected_returns.max()

    target_returns = np.linspace(min_return, max_return, points)

    frontier = []

    for target in target_returns:
        weights = minimize_volatility_for_target_return(target, expected_returns, cov_matrix)

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