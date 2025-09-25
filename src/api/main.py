from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from pydantic import BaseModel

from src.core.database import get_db
from src.core.models import CountryScore, IndustryScore, PillarScore, MetricNormalized, MetricCatalog

app = FastAPI(title="CIVI API", description="API for Critical Infrastructure Vitals Index data.")

# Pydantic Models for API Response
from pydantic import BaseModel

class CountryScoreResponse(BaseModel):
    id: int
    country_code: str
    year: int
    country_score: float

    class Config:
        from_attributes = True

class IndustryScoreResponse(BaseModel):
    id: int
    country_code: str
    year: int
    industry: str
    industry_score: float

    class Config:
        from_attributes = True

class PillarScoreResponse(BaseModel):
    id: int
    country_code: str
    year: int
    industry: str
    pillar: str
    pillar_score: float

    class Config:
        from_attributes = True

class MetricNormalizedResponse(BaseModel):
    id: int
    country_code: str
    year: int
    metric_id: str
    normalized_value: float
    normalization_method: Optional[str]
    normalization_window: Optional[str]

    class Config:
        from_attributes = True

class MetricCatalogResponse(BaseModel):
    metric_id: str
    name: str
    description: Optional[str]
    industry: str
    pillar: str
    units: Optional[str]
    directionality: Optional[str]
    source: Optional[str]
    source_url: Optional[str]
    coverage_notes: Optional[str]

    class Config:
        from_attributes = True

# Helper to convert SQLAlchemy model to Pydantic model
def to_pydantic(model, data):
    return model(**{c.name: getattr(data, c.name) for c in model.__table__.columns})

@app.get("/countries", response_model=List[CountryScoreResponse])
def get_countries(year: Optional[int] = None, db: Session = Depends(get_db)):
    """Retrieve a list of countries with their overall CIVI scores."""
    query = db.query(CountryScore)
    if year:
        query = query.filter(CountryScore.year == year)
    return query.all()

@app.get("/countries/{country_code}")
def get_country_profile(
    country_code: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Retrieve a detailed profile for a specific country, including industry, pillar, and metric scores."""
    country_code = country_code.upper()

    country_scores_query = db.query(CountryScore).filter(CountryScore.country_code == country_code)
    industry_scores_query = db.query(IndustryScore).filter(IndustryScore.country_code == country_code)
    pillar_scores_query = db.query(PillarScore).filter(PillarScore.country_code == country_code)
    metric_normalized_query = db.query(MetricNormalized).filter(MetricNormalized.country_code == country_code)
    metric_catalog_query = db.query(MetricCatalog)

    if year:
        country_scores_query = country_scores_query.filter(CountryScore.year == year)
        industry_scores_query = industry_scores_query.filter(IndustryScore.year == year)
        pillar_scores_query = pillar_scores_query.filter(PillarScore.year == year)
        metric_normalized_query = metric_normalized_query.filter(MetricNormalized.year == year)

    country_scores = country_scores_query.all()
    industry_scores = industry_scores_query.all()
    pillar_scores = pillar_scores_query.all()
    metric_normalized = metric_normalized_query.all()
    metric_catalog = metric_catalog_query.all()

    if not country_scores and not industry_scores and not pillar_scores and not metric_normalized:
        raise HTTPException(status_code=404, detail="Country data not found.")

    # Join metric_normalized with metric_catalog to get industry/pillar for metrics
    df_metrics = pd.DataFrame([m.__dict__ for m in metric_normalized])
    df_catalog = pd.DataFrame([c.__dict__ for c in metric_catalog])
    df_metrics = df_metrics.drop(columns=['_sa_instance_state'], errors='ignore')
    df_catalog = df_catalog.drop(columns=['_sa_instance_state'], errors='ignore')

    df_metrics_detailed = pd.merge(df_metrics, df_catalog[['metric_id', 'name', 'industry', 'pillar', 'units']], on='metric_id', how='left')

    return {
        "country_code": country_code,
        "country_scores": country_scores,
        "industry_scores": industry_scores,
        "pillar_scores": pillar_scores,
        "metrics": df_metrics_detailed.to_dict(orient="records")
    }

@app.get("/industries/{industry_name}", response_model=List[IndustryScoreResponse])
def get_industry_comparison(
    industry_name: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Compare countries for a specific industry."""
    query = db.query(IndustryScore).filter(IndustryScore.industry == industry_name)
    if year:
        query = query.filter(IndustryScore.year == year)
    return query.all()

@app.get("/pillars/{pillar_name}", response_model=List[PillarScoreResponse])
def get_pillar_comparison(
    pillar_name: str,
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Compare countries for a specific pillar."""
    query = db.query(PillarScore).filter(PillarScore.pillar == pillar_name)
    if year:
        query = query.filter(PillarScore.year == year)
    return query.all()

@app.get("/scores/timeseries", response_model=List[dict])
def get_timeseries(
    country: str,
    industry: Optional[str] = None,
    pillar: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Return a trend line for a specific country, optionally filtered by industry and/or pillar."""
    country = country.upper()

    if industry and pillar:
        query = db.query(PillarScore).filter(
            PillarScore.country_code == country,
            PillarScore.industry == industry,
            PillarScore.pillar == pillar
        ).order_by(PillarScore.year)
        results = query.all()
        return [{'year': r.year, 'score': r.pillar_score} for r in results]
    elif industry:
        query = db.query(IndustryScore).filter(
            IndustryScore.country_code == country,
            IndustryScore.industry == industry
        ).order_by(IndustryScore.year)
        results = query.all()
        return [{'year': r.year, 'score': r.industry_score} for r in results]
    elif country:
        query = db.query(CountryScore).filter(
            CountryScore.country_code == country
        ).order_by(CountryScore.year)
        results = query.all()
        return [{'year': r.year, 'score': r.country_score} for r in results]
    
    raise HTTPException(status_code=400, detail="Invalid query. Please provide at least a country.")
