import os
import json
import pandas as pd
from config import INDICATORS

RAW_DATA_DIR = "../data/raw"
INTERIM_DATA_DIR = "../data/interim"
os.makedirs(INTERIM_DATA_DIR, exist_ok=True)

def _load_json_file(filepath):
    """Helper to load JSON data from a file."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def _save_cleaned_data(df, indicator_key):
    """Helper to save cleaned data as CSV."""
    filepath = os.path.join(INTERIM_DATA_DIR, f"{indicator_key}.csv")
    df.to_csv(filepath, index=False)
    print(f"  Saved cleaned data for {indicator_key} to {filepath}")

def _clean_world_bank_data(indicator_key):
    """Cleans World Bank data."""
    filepath = os.path.join(RAW_DATA_DIR, "world_bank", f"{indicator_key}.json")
    data = _load_json_file(filepath)
    if data:
        # World Bank data structure: list of dicts, each with 'country', 'date', 'value'
        # Explicitly construct DataFrame to avoid ValueError
        records = []
        for item in data:
            if isinstance(item, dict):
                records.append({
                    'country_iso': item.get('countryiso3code'),
                    'year': item.get('date'),
                    'value': item.get('value')
                })
        df = pd.DataFrame(records)

        if not df.empty:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df.dropna(subset=['country_iso', 'year', 'value'], inplace=True)
            _save_cleaned_data(df, indicator_key)
        else:
            print(f"  No data to clean for {indicator_key} from World Bank.")
    else:
        print(f"  Raw data not found for {indicator_key} from World Bank.")

def _clean_fao_data(indicator_key):
    """Cleans FAO data (dummy for now)."""
    filepath = os.path.join(RAW_DATA_DIR, "fao", f"{indicator_key}.json")
    data = _load_json_file(filepath)
    if data:
        # Assuming FAO dummy data has a 'data' key with list of dicts
        if 'data' in data and data['data']:
            df = pd.DataFrame(data['data'])
            if not df.empty:
                df = df[['country', 'year', 'value']]
                df.columns = ['country_iso', 'year', 'value']
                df['year'] = pd.to_numeric(df['year'], errors='coerce')
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df.dropna(subset=['country_iso', 'year', 'value'], inplace=True)
                _save_cleaned_data(df, indicator_key)
            else:
                print(f"  No data to clean for {indicator_key} from FAO.")
        else:
            print(f"  FAO raw data for {indicator_key} is empty or malformed.")
    else:
        print(f"  Raw data not found for {indicator_key} from FAO.")

def _clean_dummy_data(indicator_key, source_name):
    """Cleans dummy data."""
    filepath = os.path.join(RAW_DATA_DIR, source_name.lower().replace(" ", "_"), f"{indicator_key}_dummy.json")
    data = _load_json_file(filepath)
    if data and 'data' in data and data['data']:
        df = pd.DataFrame(data['data'])
        if not df.empty:
            df = df[['country', 'year', 'value']]
            df.columns = ['country_iso', 'year', 'value']
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df.dropna(subset=['country_iso', 'year', 'value'], inplace=True)
            _save_cleaned_data(df, indicator_key)
        else:
            print(f"  No data to clean for {indicator_key} from {source_name}.")
    else:
        print(f"  Raw data not found or is empty for {indicator_key} from {source_name}.")

def clean_all():
    print("Starting raw data cleaning process...")
    for industry, pillars_data in INDICATORS.items():
        for pillar, indicators_list in pillars_data.items():
            for indicator in indicators_list:
                source_name = indicator["source"].split('/')[0].strip().lower()
                indicator_key = indicator["key"]
                print(f"Cleaning data for indicator: {indicator_key}")

                if "world bank" in source_name:
                    _clean_world_bank_data(indicator_key)
                elif "fao" in source_name:
                    _clean_fao_data(indicator_key)
                else:
                    _clean_dummy_data(indicator_key, indicator["source"])
    print("Raw data cleaning process complete.")

if __name__ == "__main__":
    clean_all()