import os
import pandas as pd
import yfinance as yf
from datetime import datetime

# Define the list of mutual funds and benchmark indices to download
MUTUAL_FUNDS = {
    "VFIAX": "Vanguard 500 Index Fund (Large Cap Blend)",
    "VTSAX": "Vanguard Total Stock Market (Broad Market)",
    "VGSLX": "Vanguard Real Estate Index (Real Estate)",
    "VBTLX": "Vanguard Total Bond Market (Fixed Income)",
    "VIGAX": "Vanguard Growth Index (Large Cap Growth)",
    "VWELX": "Vanguard Wellington Fund (Balanced/Hybrid)"
}

BENCHMARKS = {
    "^GSPC": "S&P 500 Index",
    "^IXIC": "NASDAQ Composite"
}

def collect_financial_data(start_date="2021-01-01", end_date=None):
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
        
    print(f"Starting data collection from {start_date} to {end_date}...")
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Combine tickers
    all_tickers = {**MUTUAL_FUNDS, **BENCHMARKS}
    
    # Dictionary to hold dataframes for combining
    combined_data = {}
    
    for ticker, name in all_tickers.items():
        print(f"Downloading data for {ticker} ({name})...")
        try:
            # Fetch historical data
            df = yf.download(ticker, start=start_date, end=end_date)
            
            if df.empty:
                print(f"Warning: No data retrieved for {ticker}")
                continue
                
            # Save individual asset data
            file_path = os.path.join(data_dir, f"{ticker.replace('^', '')}.csv")
            df.to_csv(file_path)
            print(f"Saved {ticker} data to {file_path} (Shape: {df.shape})")
            
            # Store Close/Adj Close for the combined dataset
            # Handle multi-level columns if returned by yfinance
            close_col = None
            if isinstance(df.columns, pd.MultiIndex):
                for metric in ['Close', 'Adj Close']:
                    if (metric, ticker) in df.columns:
                        close_col = df[(metric, ticker)]
                        break
            else:
                for metric in ['Close', 'Adj Close']:
                    if metric in df.columns:
                        close_col = df[metric]
                        break
            
            if close_col is not None:
                combined_data[ticker] = close_col
            else:
                raise ValueError(f"Could not find Close or Adj Close column in {df.columns}")
            
        except Exception as e:
            print(f"Error downloading {ticker}: {str(e)}")
            
    # Create combined dataframe
    if combined_data:
        combined_df = pd.DataFrame(combined_data)
        # Drop rows where all elements are NaN
        combined_df.dropna(how='all', inplace=True)
        
        combined_file_path = os.path.join(data_dir, "combined_navs.csv")
        combined_df.to_csv(combined_file_path)
        print(f"\nSaved combined NAVs to {combined_file_path} (Shape: {combined_df.shape})")
        
        # Calculate daily returns
        returns_df = combined_df.pct_change().dropna()
        returns_file_path = os.path.join(data_dir, "daily_returns.csv")
        returns_df.to_csv(returns_file_path)
        print(f"Saved daily returns to {returns_file_path} (Shape: {returns_df.shape})")
        
        # Print basic correlation matrix as a verification step
        print("\nAsset Correlation Matrix:")
        print(returns_df.corr().round(3))
        
    print("\nData collection complete!")

if __name__ == "__main__":
    collect_financial_data()
