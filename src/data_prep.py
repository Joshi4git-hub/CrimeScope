import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "crimes.csv")
DEFAULT_PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "crimes_cleaned.parquet")

# Global in-memory cache for ultra-fast callback filtering
_CACHED_DF = None
_PROCESSING_STATS = {}

def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

def clean_and_process_data(raw_path=None, processed_path=None):
    """
    Cleans raw Chicago Crime data, derives temporal features, standardizes types,
    groups rare crime categories into 'OTHER', and caches output.
    """
    global _CACHED_DF, _PROCESSING_STATS
    
    if raw_path is None:
        raw_path = DEFAULT_RAW_PATH
    if processed_path is None:
        processed_path = DEFAULT_PROCESSED_PATH

    logs = []
    logs.append(f"Starting data preprocessing on: {raw_path}")
    
    if not os.path.exists(raw_path):
        logs.append("Raw file not found. Generating sample data...")
        from scripts.make_sample_data import generate_sample_crimes
        df = generate_sample_crimes(num_rows=50000, output_path=raw_path)
    else:
        df = pd.read_csv(raw_path)
        
    initial_rows = len(df)
    logs.append(f"Loaded raw dataset with {initial_rows:,} rows and {len(df.columns)} columns.")
    
    # Standardize column names (lowercase with underscores)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Rename common variants if needed
    col_mapping = {
        "primary_type": "primary_type",
        "location_description": "location_description",
        "community_area": "community_area",
        "x_coordinate": "x_coordinate",
        "y_coordinate": "y_coordinate"
    }
    df = df.rename(columns=col_mapping)
    
    # 1. Parse Dates
    logs.append("Parsing date timestamps and deriving time features...")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Drop invalid dates
    df = df.dropna(subset=["date"])
    
    # Derive temporal columns
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["day_of_week"] = df["date"].dt.strftime("%a")
    df["day_of_week_num"] = df["date"].dt.dayofweek  # 0=Monday, 6=Sunday
    df["hour"] = df["date"].dt.hour
    df["is_weekend"] = df["day_of_week_num"] >= 5
    df["season"] = df["month"].apply(get_season)
    
    # 2. Drop duplicates & missing critical fields
    logs.append("Cleaning missing values and duplicate rows...")
    df = df.drop_duplicates()
    critical_cols = ["latitude", "longitude", "district", "primary_type"]
    for c in critical_cols:
        if c in df.columns:
            df = df.dropna(subset=[c])
            
    # Filter valid lat/lon for Chicago
    df = df[(df["latitude"] >= 41.5) & (df["latitude"] <= 42.1) & 
            (df["longitude"] >= -88.1) & (df["longitude"] <= -87.4)]
    
    # 3. Cast numeric IDs
    df["district"] = pd.to_numeric(df["district"], errors="coerce").fillna(0).astype(int)
    if "community_area" in df.columns:
        df["community_area"] = pd.to_numeric(df["community_area"], errors="coerce").fillna(0).astype(int)
    else:
        df["community_area"] = 0
        
    df = df[df["district"] > 0]
    
    # 4. Convert boolean flags
    for bool_col in ["arrest", "domestic"]:
        if bool_col in df.columns:
            if df[bool_col].dtype == object:
                df[bool_col] = df[bool_col].astype(str).str.upper().isin(["TRUE", "1", "YES"])
            else:
                df[bool_col] = df[bool_col].astype(bool)
        else:
            df[bool_col] = False
            
    # 5. Group crime types outside top 12 into "OTHER"
    logs.append("Grouping crime categories outside top 12 into 'OTHER'...")
    top_12 = df["primary_type"].value_counts().nlargest(12).index.tolist()
    df["primary_type_clean"] = df["primary_type"].apply(lambda x: x if x in top_12 else "OTHER")
    
    processed_rows = len(df)
    logs.append(f"Preprocessing completed. Final row count: {processed_rows:,} (Removed {initial_rows - processed_rows:,} invalid/duplicate rows).")
    
    # Save processed dataframe
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    try:
        df.to_parquet(processed_path, index=False)
        logs.append(f"Saved processed data to Parquet: {processed_path}")
    except Exception as e:
        csv_path = processed_path.replace(".parquet", ".csv")
        df.to_csv(csv_path, index=False)
        logs.append(f"Saved processed data to CSV fallback: {csv_path}")
        
    _PROCESSING_STATS = {
        "initial_rows": initial_rows,
        "processed_rows": processed_rows,
        "removed_rows": initial_rows - processed_rows,
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "top_crimes": top_12,
        "logs": logs
    }
    
    _CACHED_DF = df
    return df

def get_processed_data(force_reload=False, raw_path=None, processed_path=None):
    """
    Returns cached DataFrame in memory for sub-second filter performance.
    """
    global _CACHED_DF
    if raw_path is None:
        raw_path = DEFAULT_RAW_PATH
    if processed_path is None:
        processed_path = DEFAULT_PROCESSED_PATH

    if _CACHED_DF is not None and not force_reload:
        return _CACHED_DF
        
    if os.path.exists(processed_path) and not force_reload:
        try:
            _CACHED_DF = pd.read_parquet(processed_path)
            return _CACHED_DF
        except Exception:
            pass
            
    return clean_and_process_data(raw_path=raw_path, processed_path=processed_path)

def get_data_summary():
    """
    Returns summary metrics and logs for data preprocessing.
    """
    global _PROCESSING_STATS
    if not _PROCESSING_STATS:
        get_processed_data()
    return _PROCESSING_STATS

if __name__ == "__main__":
    df = clean_and_process_data()
    print("Done! Head:")
    print(df[["date", "primary_type_clean", "district", "hour", "day_of_week", "is_weekend"]].head())
