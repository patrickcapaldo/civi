from fetch_data import fetch_all
from clean_data import clean_all
from process_data import process_all
from score_data import score_all
from build_json import build_all

def update_all():
    """Orchestrates the entire data pipeline."""
    print("Starting CIVI data update...")
    fetch_all()
    clean_all()
    process_all()
    score_all()
    build_all()
    print("CIVI data update complete.")

if __name__ == "__main__":
    update_all()
