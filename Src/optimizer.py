import pandas as pd
from pathlib import Path

def generate_time_horizon_portfolio(csv_path: Path):
    print(f"Loading data from {csv_path.name}...\n")
    df = pd.read_csv(csv_path)
    
    # Calculate Risk-Adjusted Return proxy
    df['Risk_Adj_Return'] = df['Total_Return_1Y'] / df['Annual_Volatility']
    
    # -----------------------------------------
    # PARTITION 1: LONG-TERM CORE (Low Risk)
    # -----------------------------------------
    # Rule: Volatility < 0.28 AND Positive 1-Year Return
    core_candidates = df[(df['Annual_Volatility'] < 0.28) & (df['Total_Return_1Y'] > 0)]
    
    # Sort by lowest volatility to ensure safety, pick the top 3
    long_term_portfolio = core_candidates.sort_values(by="Annual_Volatility", ascending=True).head(3)
    long_term_portfolio['Strategy'] = 'Long-Term Core'

    # -----------------------------------------
    # PARTITION 2: SHORT-TERM TACTICAL (High Momentum)
    # -----------------------------------------
    # Rule: Volatility >= 0.28 AND Current Price trending above 50-Day Moving Average
    tactical_candidates = df[
        (df['Annual_Volatility'] >= 0.28) & 
        (df['Current_Price_ZAc'] > df['50_Day_MA']) &
        (df['Total_Return_1Y'] > 0)
    ]
    
    # Sort by highest Risk-Adjusted Return for explosive growth, pick the top 2
    short_term_portfolio = tactical_candidates.sort_values(by="Risk_Adj_Return", ascending=False).head(2)
    short_term_portfolio['Strategy'] = 'Short-Term Tactical'

    # Combine the partitions
    final_portfolio = pd.concat([long_term_portfolio, short_term_portfolio])
    
    return final_portfolio

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    input_file = project_root / "data" / "processed" / "initial_screener_results.csv"
    
    if not input_file.exists():
        print(f"[ERROR] Could not find data file at: {input_file}")
    else:
        optimal_portfolio = generate_time_horizon_portfolio(input_file)
        
        print("--- R100k Recommended Split (Core-Satellite Strategy) ---")
        # Displaying the recommended strategy alongside the company data
        cols_to_show = ['Ticker', 'Company_Name', 'Strategy', 'Annual_Volatility', 'Total_Return_1Y']
        
        # If 'Company_Name' isn't in your CSV yet from previous steps, we drop it to avoid errors
        if 'Company_Name' not in optimal_portfolio.columns:
            cols_to_show.remove('Company_Name')
            
        print(optimal_portfolio[cols_to_show].to_string(index=False))
        
        output_file = project_root / "data" / "processed" / "recommended_portfolio.csv"
        optimal_portfolio.to_csv(output_file, index=False)