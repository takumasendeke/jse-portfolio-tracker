import yfinance as yf
import pandas as pd
import numpy as np

# Import your new custom math functions
from metrics import calculate_annual_volatility, calculate_sharpe_ratio, get_moving_average

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
            
            # Use metrics.py for calculations
            hist['50_Day_MA'] = get_moving_average(hist['Close'], window=50)
            avg_daily_volatility = calculate_annual_volatility(hist['Daily_Return'])
            sharpe = calculate_sharpe_ratio(hist['Daily_Return'])
            
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
    # --- Banking & Financial Services ---
    "FSR.JO",  # FirstRand (Banking)
    "SBK.JO",  # Standard Bank (Banking)
    "CPI.JO",  # Capitec Bank (Banking)
    "ABG.JO",  # Absa Group (Banking)
    "NED.JO",  # Nedbank Group (Banking)
    "SLM.JO",  # Sanlam (Insurance / Financials)
    "DSY.JO",  # Discovery (Insurance / Financials)
    
    # --- Technology & Media ---
    "NPN.JO",  # Naspers (Tech / Internet Investments)
    "PRX.JO",  # Prosus (Tech / Internet Investments)
    
    # --- Mining & Basic Materials (Resources) ---
    "AGL.JO",  # Anglo American (Diversified Mining)
    "GFI.JO",  # Gold Fields (Gold Mining)
    "ANG.JO",  # AngloGold Ashanti (Gold Mining)
    "SSW.JO",  # Sibanye Stillwater (PGMs and Gold)
    "IMP.JO",  # Impala Platinum (PGMs)
    "BHG.JO",  # BHP Group (Diversified Mining)
    "SOL.JO",  # Sasol (Energy & Chemicals)
    
    # --- Retail & Consumer Staples ---
    "SHP.JO",  # Shoprite Holdings (Food Retail)
    "WHL.JO",  # Woolworths Holdings (Premium Retail / Apparel)
    "PIK.JO",  # Pick n Pay Stores (Food Retail)
    "MRP.JO",  # Mr Price Group (Apparel Retail)
    "CLC.JO",  # Clicks Group (Pharmacy / Health Retail)
    "BID.JO",  # Bidcorp (Foodservice)
    
    # --- Telecommunications ---
    "VOD.JO",  # Vodacom Group (Telecoms)
    "MTN.JO",  # MTN Group (Telecoms)
    "TKG.JO",  # Telkom SA (Telecoms)

    # --- Healthcare ---
    "APN.JO",  # Aspen Pharmacare (Pharmaceuticals)
    "NTC.JO",  # Netcare (Hospitals / Healthcare Services)
    
    # --- Industrials & Real Estate ---
    "BVT.JO",  # Bidvest Group (Diversified Industrials)
    "GRT.JO",  # Growthpoint Properties (Real Estate Investment Trust - REIT)
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