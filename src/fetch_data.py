import os

def fetch_all():
    print("Fetching all raw data...")
    # In a real implementation, this would download data from APIs
    # and save it to the data/raw directory.
    # For now, we'll just create dummy files.
    raw_dir = "../data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, "worldbank_dummy.csv"), "w") as f:
        f.write("country_iso,indicator,value\n")
        f.write("USA,EG.ELC.ACCS.ZS,100\n")
        f.write("AUS,EG.ELC.ACCS.ZS,100\n")
    print("Raw data fetching complete.")

if __name__ == "__main__":
    fetch_all()
