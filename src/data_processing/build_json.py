import json
import os
import numpy as np
import shutil
from src.config import LAST_UPDATED, VERSION, DATA_SOURCES, INDUSTRIES, PILLARS
from src.core.database import SessionLocal
from src.core.models import CountryScore, IndustryScore, PillarScore, MetricNormalized, MetricCatalog

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
    
    # Load country code mapping
    country_codes = _load_country_codes()
    country_info_map = {
        d['alpha-3']: {
            "name": d['name'],
            "region": d.get('region', "Unknown")
        } for d in country_codes
    }

    all_civi_data_by_country_year = {}
    latest_year = 0

    with SessionLocal() as session:
        # Fetch all data from the database
        all_country_scores = session.query(CountryScore).all()
        all_industry_scores = session.query(IndustryScore).all()
        all_pillar_scores = session.query(PillarScore).all()
        all_metric_normalized = session.query(MetricNormalized).all()
        all_metric_catalog = session.query(MetricCatalog).all()

        # Convert catalog to a dict for easy lookup
        metric_catalog_map = {m.metric_id: m for m in all_metric_catalog}

        # Organize data by country and year
        for cs in all_country_scores:
            if cs.country_code not in all_civi_data_by_country_year:
                all_civi_data_by_country_year[cs.country_code] = {}
            if cs.year not in all_civi_data_by_country_year[cs.country_code]:
                all_civi_data_by_country_year[cs.country_code][cs.year] = {"scores": {}, "industries": {}}
            all_civi_data_by_country_year[cs.country_code][cs.year]["scores"]["overall"] = cs.country_score
            latest_year = max(latest_year, cs.year)

        for ind_s in all_industry_scores:
            if ind_s.country_code not in all_civi_data_by_country_year:
                all_civi_data_by_country_year[ind_s.country_code] = {}
            if ind_s.year not in all_civi_data_by_country_year[ind_s.country_code]:
                all_civi_data_by_country_year[ind_s.country_code][ind_s.year] = {"scores": {}, "industries": {}}
            if ind_s.industry not in all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"]:
                all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"][ind_s.industry] = {"scores": {}, "pillars": {}, "indicators": []}
            all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"][ind_s.industry]["scores"]["overall"] = ind_s.industry_score
            latest_year = max(latest_year, ind_s.year)

        for p_s in all_pillar_scores:
            if p_s.country_code not in all_civi_data_by_country_year:
                all_civi_data_by_country_year[p_s.country_code] = {}
            if p_s.year not in all_civi_data_by_country_year[p_s.country_code]:
                all_civi_data_by_country_year[p_s.country_code][p_s.year] = {"scores": {}, "industries": {}}
            if p_s.industry not in all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"]:
                all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][p_s.industry] = {"scores": {}, "pillars": {}, "indicators": []}
            if p_s.pillar not in all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][p_s.industry]["pillars"]:
                all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][p_s.industry]["pillars"][p_s.pillar] = {"scores": {}}
            all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][p_s.industry]["pillars"][p_s.pillar]["scores"]["overall"] = p_s.pillar_score
            all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][p_s.industry]["scores"][p_s.pillar] = p_s.pillar_score # For direct access
            latest_year = max(latest_year, p_s.year)

        for mn in all_metric_normalized:
            metric_info = metric_catalog_map.get(mn.metric_id)
            if not metric_info: # Skip if metric not in catalog
                continue 

            if mn.country_code not in all_civi_data_by_country_year:
                all_civi_data_by_country_year[mn.country_code] = {}
            if mn.year not in all_civi_data_by_country_year[mn.country_code]:
                all_civi_data_by_country_year[mn.country_code][mn.year] = {"scores": {}, "industries": {}}
            
            industry_key = metric_info.industry.lower().replace(" ", "_").replace("&", "and") # Standardize industry key
            if industry_key not in all_civi_data_by_country_year[mn.country_code][mn.year]["industries"]:
                all_civi_data_by_country_year[mn.country_code][mn.year]["industries"][industry_key] = {"scores": {}, "pillars": {}, "indicators": []}
            
            all_civi_data_by_country_year[mn.country_code][mn.year]["industries"][industry_key]["indicators"].append({
                "key": mn.metric_id,
                "description": metric_info.name, # Using name as description for now
                "value": mn.normalized_value,
                "weight": 1, # Assuming equal weight for now, can be added to catalog
                "source": metric_info.source, # Use source from catalog
                "year": mn.year,
                "pillar": metric_info.pillar.lower()
            })
            latest_year = max(latest_year, mn.year)


    final_countries_data = {}
    for iso3, years_data in all_civi_data_by_country_year.items():
        info = country_info_map.get(iso3, {"name": iso3, "region": "Unknown"})

        # Get data for the latest year for top-level scores and industries
        latest_data = years_data.get(latest_year, {"scores": {}, "industries": {}})
        
        # Prepare historical scores array
        historical_scores_list = []
        for year in sorted(years_data.keys()):
            year_data = years_data[year]
            # Ensure all industries and pillars are present for consistency
            # This part needs to be careful not to overwrite actual data with empty dicts
            # It's more about ensuring the structure is consistent for the frontend
            current_year_industries = {}
            for ind_name in INDUSTRIES:
                ind_key = ind_name.lower().replace(" ", "_").replace("&", "and")
                current_year_industries[ind_key] = year_data["industries"].get(ind_key, {"scores": {}, "pillars": {}, "indicators": []})
                # Ensure pillars are also consistent
                current_year_pillars = {}
                for p_name in PILLARS:
                    current_year_pillars[p_name] = current_year_industries[ind_key]["pillars"].get(p_name, {"scores": {}})
                current_year_industries[ind_key]["pillars"] = current_year_pillars

            historical_scores_list.append({
                "year": year,
                "scores": year_data["scores"], # Overall scores for the year
                "industries": current_year_industries # Industry data for the year
            })

        # Prepare latest year scores for direct access
        latest_overall_scores = latest_data["scores"]
        latest_industries_data = {}
        for ind_name in INDUSTRIES:
            ind_key = ind_name.lower().replace(" ", "_").replace("&", "and")
            latest_industries_data[ind_key] = latest_data["industries"].get(ind_key, {"scores": {}, "pillars": {}, "indicators": []})
            # Ensure pillars are also consistent for the latest data
            current_latest_pillars = {}
            for p_name in PILLARS:
                current_latest_pillars[p_name] = latest_industries_data[ind_key]["pillars"].get(p_name, {"scores": {}})
            latest_industries_data[ind_key]["pillars"] = current_latest_pillars


        final_countries_data[iso3] = {
            "name": info['name'],
            "region": info['region'],
            "scores": latest_overall_scores, # Latest year's overall scores
            "industries": latest_industries_data, # Latest year's industry data
            "historical_scores": historical_scores_list # All historical data
        }

    # Verification step (simplified as INDUSTRIES is now from config)
    for industry in INDUSTRIES:
        for iso3, data in final_countries_data.items():
            ind_key = industry.lower().replace(" ", "_").replace("&", "and")
            if ind_key not in data['industries']:
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