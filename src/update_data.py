from fetch_data import fetch_all, indicator_api_map
from config import INDICATORS
from clean_data import clean_all
from process_data import process_all
from score_data import score_all
from build_json import build_all

def print_data_status():
    """Prints a report on the status of the data sources."""
    print("\n--- Data Source Status Report ---")
    total_indicators = 0
    real_data_count = 0
    for industry, pillars in INDICATORS.items():
        for pillar, indicators in pillars.items():
            for indicator in indicators:
                total_indicators += 1
                key = indicator["key"]
                if key in indicator_api_map:
                    source_info = indicator_api_map[key]
                    source = source_info.get("source", "")
                    if source in ["world_bank", "fao", "itu", "un_comtrade"]:
                        real_data_count += 1
                        status = "REAL"
                    else:
                        status = "DUMMY"
                else:
                    status = "DUMMY"
                print(f"{industry[:15]:<15} {pillar[:15]:<15} {key[:30]:<30} {status}")

    print("\n--- Summary ---")
    print(f"Total Indicators: {total_indicators}")
    print(f"Indicators with Real Data: {real_data_count}")
    print(f"Data Coverage: {real_data_count / total_indicators:.1%}")

def update_all():
    """Orchestrates the entire data pipeline."""
    print("Starting CIVI data update...")
    fetch_all()
    clean_all()
    process_all()
    score_all()
    build_all()
    print_data_status()
    print("CIVI data update complete.")

if __name__ == "__main__":
    update_all()

