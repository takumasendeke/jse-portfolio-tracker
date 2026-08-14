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
                
            # Fetch company name dynamically from Yahoo Finance
            # We check shortName first, then longName, and fallback to the ticker if both fail
            info = stock.info
            company_name = info.get('shortName') or info.get('longName') or ticker
            
            # Calculate Daily Returns
            hist['Daily_Return'] = hist['Close'].pct_change()
            
            # Use metrics.py for calculations (assuming you imported them)
            hist['50_Day_MA'] = get_moving_average(hist['Close'], window=50)
            avg_daily_volatility = calculate_annual_volatility(hist['Daily_Return'])
            sharpe = calculate_sharpe_ratio(hist['Daily_Return'])
            
            # Extract current price
            current_price = hist['Close'].iloc[-1]
            
            metrics.append({
                'Ticker': ticker,
                'Company_Name': company_name,  # <-- Added this line
                'Current_Price_ZAc': round(current_price, 2),
                'Annual_Volatility': round(avg_daily_volatility, 4),
                '50_Day_MA': round(hist['50_Day_MA'].iloc[-1], 2),
                'Total_Return_1Y': round((current_price / hist['Close'].iloc[0]) - 1, 4)
            })
            
            print(f"Successfully processed {ticker} - {company_name}")
            
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")

    # Compile into a DataFrame for easy viewing and exporting
    results_df = pd.DataFrame(metrics)
    return results_df

from pathlib import Path

if __name__ == "__main__":
    target_companies = [
        # Banking & Financials
        "FSR.JO", "SBK.JO", "CPI.JO", "ABG.JO", "NED.JO", "SLM.JO", "DSY.JO", "INL.JO", "INP.JO", "OUT.JO", "RMI.JO",
        # Tech & Media
        "NPN.JO", "PRX.JO", "BKG.JO", "DTC.JO",
        # Mining & Resources
        "AGL.JO", "GFI.JO", "ANG.JO", "SSW.JO", "IMP.JO", "BHG.JO", "SOL.JO", "NHM.JO", "ARI.JO", "KIO.JO", "EXX.JO", "DRD.JO", "MRF.JO", "HAR.JO",
        # Retail & Consumer
        "SHP.JO", "WHL.JO", "PIK.JO", "MRP.JO", "BID.JO", "CLC.JO", "SPP.JO", "TFG.JO", "TRU.JO", "PEP.JO", "CSB.JO",
        # Telecommunications
        "VOD.JO", "MTN.JO", "TKG.JO", "BLU.JO",
        # Healthcare
        "APN.JO", "NTC.JO", "LHC.JO", "MEI.JO",
        # Industrials, Food & Packaging
        "BVT.JO", "AVI.JO", "BAW.JO", "SNT.JO", "OMU.JO", "KAP.JO", "MND.JO", "SAP.JO", "TSG.JO",
        # Real Estate (REITs)
        "GRT.JO", "RDF.JO", "RES.JO", "MAS.JO", "NEP.JO", "EQU.JO", "LTE.JO", "SAC.JO"
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