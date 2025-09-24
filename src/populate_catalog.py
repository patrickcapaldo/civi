import pandas as pd
from sqlalchemy.orm import Session
from .database import engine
from .models import MetricCatalog, MetricRaw, MetricNormalized, PillarScore, IndustryScore, CountryScore, NormalizationLog, EtlRun

# Predefined list of metrics for the catalog
METRICS = [
    # Information Technology
    {'metric_id': 'IT.NET.USER.ZS', 'name': 'Individuals using the Internet (% of population)', 'industry': 'Information Technology', 'pillar': 'Effectiveness', 'directionality': 'POS', 'source': 'World Bank', 'units': '%'},
    {'metric_id': 'IT.CEL.SETS.P2', 'name': 'Mobile cellular subscriptions (per 100 people)', 'industry': 'Information Technology', 'pillar': 'Autonomy', 'directionality': 'POS', 'source': 'World Bank', 'units': 'per 100 people'},

    # Energy
    {'metric_id': 'EG.ELC.ACCS.ZS', 'name': 'Access to electricity (% of population)', 'industry': 'Energy', 'pillar': 'Effectiveness', 'directionality': 'POS', 'source': 'World Bank', 'units': '%'},
    {'metric_id': 'EG.FEC.RNEW.ZS', 'name': 'Renewable energy consumption (% of total final energy consumption)', 'industry': 'Energy', 'pillar': 'Sustainability', 'directionality': 'POS', 'source': 'World Bank', 'units': '%'},

    # Food & Agriculture
    {'metric_id': 'FAO_FS_DEFI_P3', 'name': 'Prevalence of undernourishment (% of population) (3-year average)', 'industry': 'Food & Agriculture', 'pillar': 'Resilience', 'directionality': 'NEG', 'source': 'FAOSTAT', 'units': '%'},
    {'metric_id': 'AG.PRD.FOOD.XD', 'name': 'Food production index (2014-2016 = 100)', 'industry': 'Food & Agriculture', 'pillar': 'Effectiveness', 'directionality': 'POS', 'source': 'World Bank', 'units': 'index'},

    # Healthcare
    {'metric_id': 'SH.XPD.CHEX.GD.ZS', 'name': 'Current health expenditure (% of GDP)', 'industry': 'Healthcare', 'pillar': 'Autonomy', 'directionality': 'POS', 'source': 'World Bank', 'units': '%'},
    {'metric_id': 'FAOSTAT_SDG_2_1_1_SN_ITK_DEFC', 'name': 'Prevalence of undernourishment (% of population) (SDG 2.1.1)', 'industry': 'Food & Agriculture', 'pillar': 'Resilience', 'directionality': 'NEG', 'source': 'FAOSTAT (SDMX)', 'units': '%'},
    {'metric_id': 'SH.DYN.MORT', 'name': 'Mortality rate, under-5 (per 1,000 live births)', 'industry': 'Healthcare', 'pillar': 'Effectiveness', 'directionality': 'NEG', 'source': 'World Bank', 'units': 'per 1000 live births'},
]

def populate_metrics_catalog():
    """Populates the metrics_catalog table from a predefined list."""
    df = pd.DataFrame(METRICS)
    
    with Session(engine) as session:
        # Clear related tables first to avoid foreign key constraint violations
        session.query(MetricRaw).delete()
        session.query(MetricNormalized).delete()
        session.query(PillarScore).delete()
        session.query(IndustryScore).delete()
        session.query(CountryScore).delete()
        session.query(NormalizationLog).delete()
        session.query(EtlRun).delete()
        session.query(MetricCatalog).delete()
        
        # Bulk insert new metrics
        session.bulk_insert_mappings(MetricCatalog, df.to_dict(orient="records"))
        session.commit()
        print(f"Successfully populated metrics_catalog with {len(df)} metrics.")

if __name__ == "__main__":
    populate_metrics_catalog()
