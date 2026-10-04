import os
import sys
import requests
import pandas as pd
from make_sample_data import generate_sample_crimes

def download_chicago_crimes(output_path="data/raw/crimes.csv", max_records=100000):
    """
    Downloads Chicago Crimes dataset from City of Chicago Socrata API (2020-2024).
    If network issue or timeout occurs, falls back to make_sample_data.py.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    base_url = "https://data.cityofchicago.org/resource/ijzp-q8t2.csv"
    where_clause = "year >= 2020 and year <= 2024"
    limit = 20000
    offset = 0
    all_dfs = []
    
    print("Attempting to download data from Chicago Data Portal (2020-2024)...")
    try:
        while offset < max_records:
            params = {
                "$where": where_clause,
                "$limit": limit,
                "$offset": offset,
                "$order": "date DESC"
            }
            response = requests.get(base_url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"API returned status {response.status_code}. Falling back to synthetic data generation.")
                break
            
            # Read CSV chunk
            from io import StringIO
            chunk_df = pd.read_csv(StringIO(response.text))
            if chunk_df.empty:
                break
                
            all_dfs.append(chunk_df)
            offset += len(chunk_df)
            print(f"Downloaded {offset} rows...")
            if len(chunk_df) < limit:
                break
                
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df.to_csv(output_path, index=False)
            print(f"Successfully downloaded {len(combined_df)} records to {output_path}")
            return combined_df
        else:
            raise Exception("No data retrieved from API.")
            
    except Exception as e:
        print(f"Download from Socrata API failed ({e}). Generating fallback synthetic dataset...")
        return generate_sample_crimes(num_rows=50000, output_path=output_path)

if __name__ == "__main__":
    download_chicago_crimes()
