import json
import os
import numpy as np
from config import LAST_UPDATED, VERSION, DATA_SOURCES
from score_data import score_all

DATA_DIR = "./data"
FRONTEND_PUBLIC_DATA_DIR = "../frontend/public/data"

def _load_country_codes():
    """Loads country codes and names from country-codes.json."""
    filepath = os.path.join(FRONTEND_PUBLIC_DATA_DIR, "country-codes.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def _convert_nan_to_none(obj):
    """Recursively converts numpy.nan values to None."""
    if isinstance(obj, dict):
        return {k: _convert_nan_to_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_nan_to_none(elem) for elem in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    return obj

def build_all():
    print("Building the final civi.json database...")
    
    # Get calculated scores
    country_scores_data = score_all()

    # Load country code mapping
    country_codes = _load_country_codes()
    country_info_map = {
        d['alpha-3']: {
            "name": d['name'],
            "region": d['region'] # Assuming 'region' field exists in country-codes.json
        } for d in country_codes
    }

    final_countries_data = {}
    for iso3, data in country_scores_data.items():
        info = country_info_map.get(iso3, {"name": iso3, "region": "Unknown"}) # Default if not found
        
        final_countries_data[iso3] = {
            "name": info['name'],
            "region": info['region'],
            "scores": data['scores'],
            "industries": data['industries']
        }

    final_data = {
        "metadata": {
            "last_updated": LAST_UPDATED,
            "source_version": VERSION,
            "sources": list(DATA_SOURCES.keys())
        },
        "countries": final_countries_data
    }

    # Convert numpy.nan to None for JSON serialization
    final_data_cleaned = _convert_nan_to_none(final_data)

    output_filepath = os.path.abspath(os.path.join(DATA_DIR, "civi.json"))
    print(f"Attempting to write civi.json to: {output_filepath}")
    print(f"Content to be written (first 2 countries): {list(final_data_cleaned['countries'].items())[:2]}")
    with open(output_filepath, "w") as f:
        json.dump(final_data_cleaned, f, indent=2)

    print("civi.json built successfully.")

if __name__ == "__main__":
    build_all()