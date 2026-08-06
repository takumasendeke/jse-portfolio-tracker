import yfinance as yf
import pandas as pd
import numpy as np

def fetch_jse_data(tickers, period="1y"):
    """
    Fetches historical stock data for JSE companies and calculates basic risk metrics.
    
    Args:
        tickers (list): List of JSE tickers (must include '.JO' suffix).
        period (str): The time period to pull (e.g., '6mo', '1y', '2y').
        
    Returns:
        pd.DataFrame: A consolidated dataframe with summary metrics per ticker.
    """
    print(f"Fetching data for {len(tickers)} JSE tickers...\n")
    
    metrics = []
    
    for ticker in tickers:
        try:
            # Download historical data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                print(f"Warning: No data found for {ticker}")
                continue
                
            # Calculate Daily Returns
            hist['Daily_Return'] = hist['Close'].pct_change()
            
            # Calculate 50-Day Moving Average (momentum/trend metric)
            hist['50_Day_MA'] = hist['Close'].rolling(window=50).mean()
            
            # Extract current price and basic metrics
            current_price = hist['Close'].iloc[-1]
            
            # Annualized volatility (assuming 252 trading days in a year)
            avg_daily_volatility = hist['Daily_Return'].std() * np.sqrt(252) 
            
            metrics.append({
                'Ticker': ticker,
                'Current_Price_ZAc': round(current_price, 2),
                'Annual_Volatility': round(avg_daily_volatility, 4),
                '50_Day_MA': round(hist['50_Day_MA'].iloc[-1], 2),
                'Total_Return_1Y': round((current_price / hist['Close'].iloc[0]) - 1, 4)
            })
            
            print(f"Successfully processed {ticker}")
            
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")
            
    # Compile into a DataFrame for easy viewing and exporting
    results_df = pd.DataFrame(metrics)
    return results_df

from pathlib import Path

if __name__ == "__main__":
    target_companies = [
        "FSR.JO",  # FirstRand (Banking)
        "SBK.JO",  # Standard Bank (Banking)
        "NPN.JO",  # Naspers (Tech/Internet)
        "AGL.JO",  # Anglo American (Mining/Resources)
        "SHP.JO",  # Shoprite (Retail)
        "VOD.JO"   # Vodacom (Telecommunications)
    ]
    
    print("Running initial portfolio screen...\n")
    portfolio_metrics = fetch_jse_data(target_companies, period="1y")
    
    print("\n--- JSE Quantitative Screen Results ---")
    sorted_metrics = portfolio_metrics.sort_values(by="Annual_Volatility", ascending=True)
    print(sorted_metrics.to_string(index=False))
    
    # --- DYNAMIC PATH FIX ---
    # Finds the root folder relative to this script file
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    output_dir = project_root / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)  # Creates folders if missing
    
    output_file = output_dir / "initial_screener_results.csv"
    portfolio_metrics.to_csv(output_file, index=False)
    
    print(f"\n[SUCCESS] Screener results saved to: {output_file}")