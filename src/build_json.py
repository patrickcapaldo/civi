import json
import os
import numpy as np
import shutil
from config import LAST_UPDATED, VERSION, DATA_SOURCES, INDUSTRIES
from score_data import score_all

DATA_DIR = "./data"
FRONTEND_PUBLIC_DATA_DIR = "frontend/public"
FRONTEND_MODULAR_DATA_DIR = os.path.join(FRONTEND_PUBLIC_DATA_DIR, "civi_modular")

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
            "region": d.get('region', "Unknown") # Use .get() with a default value
        } for d in country_codes
    }

    final_countries_data = {}
    for iso3, data in country_scores_data.items():
        info = country_info_map.get(iso3, {"name": iso3, "region": "Unknown"}) # Default if not found
        
        final_countries_data[iso3] = {
            "name": info['name'],
            "region": info['region'],
            "scores": data['scores'],
            "industries": data['industries'],
            "historical_scores": data['historical_scores']
        }

    # Verification step
    for iso3, data in final_countries_data.items():
        for industry in INDUSTRIES:
            if industry not in data['industries']:
                print(f"Warning: Industry '{industry}' missing for country {iso3}")

    # Create output directory if it doesn't exist
    output_dir = os.path.abspath(os.path.join(DATA_DIR, "processed", "civi_modular"))
    os.makedirs(output_dir, exist_ok=True)

    # Save individual country data files
    for iso3, data in final_countries_data.items():
        country_filepath = os.path.join(output_dir, f"{iso3}.json")
        with open(country_filepath, "w") as f:
            json.dump(_convert_nan_to_none(data), f, indent=2)
        print(f"  Saved data for {iso3} to {country_filepath}")

    # Save metadata file
    metadata = {
        "last_updated": LAST_UPDATED,
        "source_version": VERSION,
        "sources": list(DATA_SOURCES.keys())
    }
    metadata_filepath = os.path.join(output_dir, "metadata.json")
    with open(metadata_filepath, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved metadata to {metadata_filepath}")

    print("Modular civi data built successfully.")

    # Copy modular data to frontend public directory
    if os.path.exists(FRONTEND_MODULAR_DATA_DIR):
        shutil.rmtree(FRONTEND_MODULAR_DATA_DIR)
    shutil.copytree(output_dir, FRONTEND_MODULAR_DATA_DIR)
    print(f"Copied modular data to frontend: {FRONTEND_MODULAR_DATA_DIR}")

if __name__ == "__main__":
    build_all()