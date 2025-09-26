from src.etl.fetch_data import fetch_all, indicator_api_map
from src.data_processing.create_derived_metrics import create_all_derived_metrics
from src.data_processing.process_data import process_all
from src.data_processing.score_data import score_all
from src.data_processing.build_json import build_all
from src.core.database import SessionLocal
from src.core.models import MetricCatalog

def print_data_status():
    """Prints a report on the status of the data sources based on the metrics catalog."""
    print("\n--- Data Source Status Report ---")
    with SessionLocal() as session:
        indicators = session.query(MetricCatalog).order_by(MetricCatalog.industry, MetricCatalog.pillar).all()
        
        total_indicators = len(indicators)
        real_data_count = 0
        
        for indicator in indicators:
            # A simple check to see if the source is one of the implemented real ones
            if indicator.source and indicator.source.lower() in ["world bank", "itu", "faostat", "who", "who gho", "nd-gain", "derived from world bank"]:
                status = "REAL"
                real_data_count += 1
            else:
                status = "DUMMY" # Or just print the source
            
            print(f"{indicator.industry[:15]:<15} {indicator.pillar[:15]:<15} {indicator.metric_id[:30]:<30} {indicator.source:<15} {status}")

    if total_indicators > 0:
        print("\n--- Summary ---")
        print(f"Total Indicators in Catalog: {total_indicators}")
        print(f"Indicators with Real Data Fetchers: {real_data_count}")
        print(f"Data Coverage: {real_data_count / total_indicators:.1%}")
    else:
        print("No indicators found in the catalog.")

def update_all():
    """Orchestrates the entire data pipeline."""
    print("Starting CIVI data update...")
    fetch_all()
    create_all_derived_metrics()
    # clean_all() # This step is obsolete
    process_all()
    score_all()
    build_all()
    print_data_status()
    print("CIVI data update complete.")

if __name__ == "__main__":
    update_all()