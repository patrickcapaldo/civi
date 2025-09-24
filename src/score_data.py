import pandas as pd
from sqlalchemy.orm import Session
from .database import engine
from .models import MetricCatalog, MetricNormalized, PillarScore, IndustryScore, CountryScore

def aggregate_scores():
    """Aggregates normalized metrics into pillar, industry, and country scores."""
    with Session(engine) as session:
        # Fetch all normalized data
        normalized_metrics = session.query(MetricNormalized).all()
        if not normalized_metrics:
            print("No normalized metrics to aggregate.")
            return

        df_normalized = pd.DataFrame([n.__dict__ for n in normalized_metrics])
        df_normalized = df_normalized.drop(columns=['_sa_instance_state'], errors='ignore')

        # Fetch metric catalog for industry and pillar information
        metric_catalog = session.query(MetricCatalog).all()
        df_catalog = pd.DataFrame([m.__dict__ for m in metric_catalog])
        df_catalog = df_catalog.drop(columns=['_sa_instance_state'], errors='ignore')
        df_catalog = df_catalog[['metric_id', 'industry', 'pillar']]

        df_merged = pd.merge(df_normalized, df_catalog, on='metric_id', how='left')

        # 1. Aggregate to Pillar Scores
        print("Aggregating to Pillar Scores...")
        pillar_scores = df_merged.groupby(['country_code', 'year', 'industry', 'pillar'])['normalized_value'].mean().reset_index()
        pillar_scores.rename(columns={'normalized_value': 'pillar_score'}, inplace=True)

        # 2. Aggregate to Industry Scores
        print("Aggregating to Industry Scores...")
        industry_scores = pillar_scores.groupby(['country_code', 'year', 'industry'])['pillar_score'].mean().reset_index()
        industry_scores.rename(columns={'pillar_score': 'industry_score'}, inplace=True)

        # 3. Aggregate to Country Scores
        print("Aggregating to Country Scores...")
        country_scores = industry_scores.groupby(['country_code', 'year'])['industry_score'].mean().reset_index()
        country_scores.rename(columns={'industry_score': 'country_score'}, inplace=True)

        # Clear existing scores before inserting new ones
        session.query(PillarScore).delete()
        session.query(IndustryScore).delete()
        session.query(CountryScore).delete()

        # Bulk insert into respective tables
        if not pillar_scores.empty:
            session.bulk_insert_mappings(PillarScore, pillar_scores.to_dict(orient="records"))
            print(f"Successfully inserted {len(pillar_scores)} pillar scores.")
        else:
            print("No pillar scores to insert.")

        if not industry_scores.empty:
            session.bulk_insert_mappings(IndustryScore, industry_scores.to_dict(orient="records"))
            print(f"Successfully inserted {len(industry_scores)} industry scores.")
        else:
            print("No industry scores to insert.")

        if not country_scores.empty:
            session.bulk_insert_mappings(CountryScore, country_scores.to_dict(orient="records"))
            print(f"Successfully inserted {len(country_scores)} country scores.")
        else:
            print("No country scores to insert.")

        session.commit()

if __name__ == "__main__":
    aggregate_scores()