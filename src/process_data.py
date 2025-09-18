import os
import pandas as pd
from config import INDICATORS

INTERIM_DATA_DIR = "../data/interim"
PROCESSED_DATA_DIR = "../data/processed"
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def process_all():
    print("Starting data processing...")
    all_processed_data = []

    for industry, pillars_data in INDICATORS.items():
        for pillar, indicators_list in pillars_data.items():
            for indicator in indicators_list:
                indicator_key = indicator["key"]
                filepath = os.path.join(INTERIM_DATA_DIR, f"{indicator_key}.csv")

                if os.path.exists(filepath):
                    df = pd.read_csv(filepath)
                    if not df.empty:
                        # Get the latest year's data for each country
                        df_latest = df.loc[df.groupby('country_iso')['year'].idxmax()]
                        df_latest = df_latest[['country_iso', 'value', 'year']]
                        df_latest.rename(columns={'value': indicator_key, 'year': f'{indicator_key}_year'}, inplace=True)
                        all_processed_data.append(df_latest)
                        print(f"  Processed data for indicator: {indicator_key}")
                    else:
                        print(f"  Interim data for {indicator_key} is empty.")
                else:
                    print(f"  Interim data not found for {indicator_key}.")

    if all_processed_data:
        # Merge all processed indicator data into a single DataFrame
        # Use reduce with an outer merge to keep all countries, even if they miss some indicators
        from functools import reduce
        df_final = reduce(lambda left, right: pd.merge(left, right, on='country_iso', how='outer'), all_processed_data)
        
        filepath = os.path.join(PROCESSED_DATA_DIR, "all_indicators_processed.csv")
        df_final.to_csv(filepath, index=False)
        print(f"All processed indicators saved to {filepath}")
    else:
        print("No data to process for any indicator.")

    print("Data processing complete.")

if __name__ == "__main__":
    process_all()