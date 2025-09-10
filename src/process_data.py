import os
import pandas as pd

def process_all():
    print("Processing and normalizing data...")
    # This would load interim data, normalize it, and save to data/processed.
    processed_dir = "../data/processed"
    os.makedirs(processed_dir, exist_ok=True)
    dummy_interim_path = "../data/interim/energy.csv"
    if os.path.exists(dummy_interim_path):
        df = pd.read_csv(dummy_interim_path)
        # Dummy normalization
        df['normalized_value'] = (df['value'] - df['value'].min()) / (df['value'].max() - df['value'].min()) * 100
        df.to_csv(os.path.join(processed_dir, "scores_by_indicator.csv"), index=False)
    print("Data processing complete.")

if __name__ == "__main__":
    process_all()
