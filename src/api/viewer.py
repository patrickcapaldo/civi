
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import json

from src.core.database import get_db
from src.core.models import MetricRaw, MetricCatalog

router = APIRouter()

# Load country codes for name-to-code mapping
with open("frontend/public/country-codes.json", "r") as f:
    country_codes = json.load(f)

country_name_to_code_map = {country["name"]: country["alpha-3"] for country in country_codes}

@router.get("/api/data")
def get_spreadsheet_data(
    country_name: Optional[str] = None,
    industry: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fetch raw and catalog data for spreadsheet view, with optional filters."""
    query_raw = db.query(MetricRaw)
    query_catalog = db.query(MetricCatalog)

    if country_name:
        country_code = country_name_to_code_map.get(country_name)
        if not country_code:
            raise HTTPException(status_code=404, detail=f"Country '{country_name}' not found.")
        query_raw = query_raw.filter(MetricRaw.country_code == country_code)
    
    if industry:
        # Filter catalog first, then join with raw data
        metric_ids_in_industry = [m.metric_id for m in query_catalog.filter(MetricCatalog.industry == industry).all()]
        if not metric_ids_in_industry:
            return [] # No metrics for this industry
        query_raw = query_raw.filter(MetricRaw.metric_id.in_(metric_ids_in_industry))

    # Fetch data and convert to DataFrames
    raw_data = query_raw.all()
    catalog_data = query_catalog.all()

    if not raw_data:
        return []

    df_raw = pd.DataFrame([r.__dict__ for r in raw_data])
    df_catalog = pd.DataFrame([c.__dict__ for c in catalog_data])

    # Drop SQLAlchemy internal state columns
    df_raw = df_raw.drop(columns=['_sa_instance_state'], errors='ignore')
    df_catalog = df_catalog.drop(columns=['_sa_instance_state'], errors='ignore')

    # Merge dataframes to combine raw values with metric metadata
    df_merged = pd.merge(
        df_raw[['country_code', 'year', 'metric_id', 'metric_value', 'source']], 
        df_catalog[["metric_id", "name", "industry", "pillar", "units"]], 
        on="metric_id", 
        how="left"
    )

    # Reorder columns for better readability
    cols_to_show = [
        "country_code", "year", "industry", "pillar", "name", "metric_value", "units", "source"
    ]
    df_merged = df_merged[cols_to_show]

    return df_merged.to_dict(orient="records")
