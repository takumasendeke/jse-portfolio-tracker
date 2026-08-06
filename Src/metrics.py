import numpy as np
import pandas as pd

def calculate_annual_volatility(daily_returns, trading_days=252):
    """
    Calculates the annualized volatility of a stock based on daily returns.
    Volatility is a statistical measure of the dispersion of returns (Risk).
    """
    return daily_returns.std() * np.sqrt(trading_days)

def calculate_sharpe_ratio(daily_returns, risk_free_rate=0.08, trading_days=252):
    """
    Calculates the annualized Sharpe Ratio.
    This measures risk-adjusted return (how much excess return you receive for the extra volatility).
    Note: The South African risk-free rate is roughly 8% (0.08).
    """
    # Annualize the return
    annual_return = (1 + daily_returns.mean()) ** trading_days - 1
    
    # Annualize the volatility
    annual_vol = calculate_annual_volatility(daily_returns, trading_days)
    
    if annual_vol == 0:
        return 0.0
        
    return (annual_return - risk_free_rate) / annual_vol

def get_moving_average(prices, window=50):
    """
    Calculates the Simple Moving Average (SMA) over a specific window.
    Used for trend analysis and momentum tracking.
    """
    return prices.rolling(window=window).mean()