import os
import pandas as pd
import numpy as np
from config import PILLARS, INDUSTRIES, INDICATORS, PILLAR_WEIGHTS, INDUSTRY_WEIGHTS

PROCESSED_DATA_DIR = "../data/processed"

def _normalize_indicator(series, indicator_key):
    """Normalizes an indicator series to a 0-100 scale.
    Assumes higher values are better. Needs to be extended for 'lower is better' indicators.
    """
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series([50] * len(series), index=series.index) # Handle cases with no variation

    # Simple min-max normalization
    normalized_series = ((series - min_val) / (max_val - min_val)) * 100
    return normalized_series

def score_all():
    print("Starting CIVI score calculation...")
    filepath = os.path.join(PROCESSED_DATA_DIR, "all_indicators_processed.csv")
    if not os.path.exists(filepath):
        print(f"Error: Processed data file not found at {filepath}")
        return {}

    df_processed = pd.read_csv(filepath)
    if df_processed.empty:
        print("Processed data is empty. No scores to calculate.")
        return {}

    final_scores = {}

    # Normalize all indicator columns
    df_normalized = df_processed.copy()
    for industry, pillars_data in INDICATORS.items():
        for pillar, indicators_list in pillars_data.items():
            for indicator in indicators_list:
                indicator_key = indicator["key"]
                if indicator_key in df_normalized.columns:
                    df_normalized[indicator_key] = _normalize_indicator(df_normalized[indicator_key], indicator_key)
                else:
                    df_normalized[indicator_key] = np.nan # Ensure column exists, fill with NaN if not present

    # Iterate through each country to calculate scores
    for country_iso in df_normalized['country_iso'].unique():
        country_data = df_normalized[df_normalized['country_iso'] == country_iso].iloc[0] # Get the row for the current country
        
        country_industry_scores = {}
        country_overall_scores = {pillar: 0 for pillar in PILLARS}

        for industry in INDUSTRIES:
            industry_pillar_scores = {}
            for pillar in PILLARS:
                pillar_score = 0
                total_weight = 0
                
                # Check if industry and pillar exist in INDICATORS config
                if industry in INDICATORS and pillar in INDICATORS[industry]:
                    for indicator in INDICATORS[industry][pillar]:
                        indicator_key = indicator["key"]
                        indicator_weight = indicator["weight"]
                        
                        if pd.notna(country_data.get(indicator_key)):
                            pillar_score += country_data[indicator_key] * indicator_weight
                            total_weight += indicator_weight
                
                if total_weight > 0:
                    industry_pillar_scores[pillar] = round(pillar_score / total_weight, 2)
                else:
                    industry_pillar_scores[pillar] = np.nan # No data for this pillar

            # Calculate overall industry score for the country
            overall_industry_score = 0
            industry_total_pillar_weight = 0
            for pillar, score in industry_pillar_scores.items():
                if pd.notna(score):
                    overall_industry_score += score * PILLAR_WEIGHTS.get(pillar, 0.25) # Use default if not in config
                    industry_total_pillar_weight += PILLAR_WEIGHTS.get(pillar, 0.25)
            
            if industry_total_pillar_weight > 0:
                country_industry_scores[industry] = {"scores": {p: industry_pillar_scores.get(p, np.nan) for p in PILLARS}}
                country_industry_scores[industry]["scores"]["civi_index"] = round(overall_industry_score / industry_total_pillar_weight, 2)
            else:
                country_industry_scores[industry] = {"scores": {p: np.nan for p in PILLARS}}
                country_industry_scores[industry]["scores"]["civi_index"] = np.nan

            # Aggregate industry scores to country overall scores (for main CIVI index)
            if pd.notna(country_industry_scores[industry]["scores"]["civi_index"]):
                for pillar, score in industry_pillar_scores.items():
                    if pd.notna(score):
                        country_overall_scores[pillar] += score * INDUSTRY_WEIGHTS.get(industry, 1.0 / len(INDUSTRIES))

        # Round overall pillar scores for the country
        for pillar in PILLARS:
            if pd.notna(country_overall_scores[pillar]):
                country_overall_scores[pillar] = round(country_overall_scores[pillar], 2)

        # Calculate overall country CIVI index
        overall_civi_index = 0
        overall_civi_total_weight = 0
        for pillar, score in country_overall_scores.items():
            # This aggregation needs to be re-thought if we want a true overall CIVI from industry pillars
            # For now, let's just average the pillar scores that have data
            if pd.notna(score):
                overall_civi_index += score
                overall_civi_total_weight += 1
        
        if overall_civi_total_weight > 0:
            country_overall_scores["civi_index"] = round(overall_civi_index / overall_civi_total_weight, 2)
        else:
            country_overall_scores["civi_index"] = np.nan

        final_scores[country_iso] = {
            "name": country_iso, # Placeholder, will be updated by build_json
            "region": "Unknown", # Placeholder, will be updated by build_json
            "scores": country_overall_scores,
            "industries": country_industry_scores
        }

    print("CIVI score calculation complete.")
    print(f"Sample of calculated scores (first 2 countries): {list(final_scores.items())[:2]}")
    return final_scores

if __name__ == "__main__":
    scores = score_all()
    # For testing, print a sample
    if scores:
        print("\nSample Scores (from direct execution):")
        for iso, data in list(scores.items())[:2]: # Print first 2 countries
            print(f"Country: {iso}")
            print(f"  Overall Scores: {data['scores']}")
            for industry, ind_data in data['industries'].items():
                print(f"    Industry {industry}: {ind_data['scores']}")