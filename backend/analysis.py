import pandas as pd


def calculate_returns(price_df):
    """
    Berechnet tägliche Renditen
    """
    returns = price_df.pct_change()
    return returns.dropna()


def covariance_matrix(returns_df):
    """
    Berechnet Kovarianzmatrix für Markowitz
    """
    return returns_df.cov()


def correlation_matrix(returns_df):
    """
    Berechnet Korrelationsmatrix
    """
    return returns_df.corr()