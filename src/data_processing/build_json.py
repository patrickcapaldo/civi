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

        # Initialize structure for all countries and years that have any data
        for score_obj in all_country_scores + all_industry_scores + all_pillar_scores + all_metric_normalized:
            if score_obj.country_code not in all_civi_data_by_country_year:
                all_civi_data_by_country_year[score_obj.country_code] = {}
            if score_obj.year not in all_civi_data_by_country_year[score_obj.country_code]:
                all_civi_data_by_country_year[score_obj.country_code][score_obj.year] = {"scores": {}, "industries": {}}
            latest_year = max(latest_year, score_obj.year)

        # Populate overall country scores
        for cs in all_country_scores:
            all_civi_data_by_country_year[cs.country_code][cs.year]["scores"]["overall"] = cs.country_score

        # Populate industry scores and initialize industry structure
        for ind_s in all_industry_scores:
            industry_key = ind_s.industry.lower().replace(" ", "_").replace("&", "and")
            if industry_key not in all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"]:
                all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"][industry_key] = {"scores": {}, "pillars": {}, "indicators": []}
            all_civi_data_by_country_year[ind_s.country_code][ind_s.year]["industries"][industry_key]["scores"]["overall"] = ind_s.industry_score

        # Populate pillar scores (both overall country and within industry)
        for p_s in all_pillar_scores:
            industry_key = p_s.industry.lower().replace(" ", "_").replace("&", "and")
            pillar_key = p_s.pillar.lower()

            # Ensure industry structure exists
            if industry_key not in all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"]:
                all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][industry_key] = {"scores": {}, "pillars": {}, "indicators": []}
            
            # Store pillar score within the industry's pillar structure
            if pillar_key not in all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][industry_key]["pillars"]:
                all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][industry_key]["pillars"][pillar_key] = {"scores": {}}
            all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][industry_key]["pillars"][pillar_key]["scores"]["overall"] = p_s.pillar_score
            
            # Also store pillar score directly under industry's scores for radar chart
            all_civi_data_by_country_year[p_s.country_code][p_s.year]["industries"][industry_key]["scores"][pillar_key] = p_s.pillar_score
            
            # Aggregate pillar scores to overall country scores for the year
            all_civi_data_by_country_year[p_s.country_code][p_s.year]["scores"][pillar_key] = p_s.pillar_score

        # Populate normalized metrics (indicators)
        for mn in all_metric_normalized:
            metric_info = metric_catalog_map.get(mn.metric_id)
            if not metric_info: # Skip if metric not in catalog
                continue 
            
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


    final_countries_data = {}
    for iso3, info in country_info_map.items():
        years_data_for_country = all_civi_data_by_country_year.get(iso3, {})
        country_latest_year = max(years_data_for_country.keys()) if years_data_for_country else latest_year

        latest_overall_scores = {}
        latest_industries_data = {}

        # Calculate latest overall scores with confidence
        for pillar_key in PILLARS:
            latest_pillar_year = 0
            latest_pillar_score = None
            for year in sorted(years_data_for_country.keys(), reverse=True):
                if pillar_key in years_data_for_country[year]["scores"]:
                    latest_pillar_score = years_data_for_country[year]["scores"][pillar_key]
                    latest_pillar_year = year
                    break
            latest_overall_scores[pillar_key] = latest_pillar_score
            confidence = max(0, 1 - (country_latest_year - latest_pillar_year) * 0.1) if latest_pillar_year > 0 else 0
            latest_overall_scores[f"{pillar_key}_confidence"] = confidence

        # Calculate latest industry scores with confidence
        for ind_name in INDUSTRIES:
            ind_key = ind_name.lower().replace(" ", "_").replace("&", "and")
            latest_industries_data[ind_key] = {"scores": {}, "pillars": {}, "indicators": []}
            for pillar_key in PILLARS:
                latest_pillar_year = 0
                latest_pillar_score = None
                latest_indicators = []
                for year in sorted(years_data_for_country.keys(), reverse=True):
                    if ind_key in years_data_for_country[year]["industries"] and pillar_key in years_data_for_country[year]["industries"][ind_key]["scores"]:
                        latest_pillar_score = years_data_for_country[year]["industries"][ind_key]["scores"][pillar_key]
                        latest_pillar_year = year
                        latest_indicators = [i for i in years_data_for_country[year]["industries"][ind_key]["indicators"] if i['pillar'] == pillar_key]
                        break
                latest_industries_data[ind_key]["scores"][pillar_key] = latest_pillar_score
                confidence = max(0, 1 - (country_latest_year - latest_pillar_year) * 0.1) if latest_pillar_year > 0 else 0
                latest_industries_data[ind_key]["scores"][f"{pillar_key}_confidence"] = confidence
                if latest_indicators:
                    latest_industries_data[ind_key]["indicators"].extend(latest_indicators)

        historical_scores_list = []
        if years_data_for_country:
            for year in sorted(years_data_for_country.keys()):
                year_data = years_data_for_country[year]
                current_year_industries = {}
                for ind_name in INDUSTRIES:
                    ind_key = ind_name.lower().replace(" ", "_").replace("&", "and")
                    industry_data = year_data["industries"].get(ind_key, {"scores": {}, "pillars": {}, "indicators": []})
                    current_year_industries[ind_key] = industry_data

                historical_scores_list.append({
                    "year": year,
                    "scores": year_data.get("scores", {}),
                    "industries": current_year_industries
                })

        final_countries_data[iso3] = {
            "name": info['name'],
            "region": info['region'],
            "scores": latest_overall_scores,
            "industries": latest_industries_data,
            "historical_scores": historical_scores_list
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
