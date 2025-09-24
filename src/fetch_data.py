import requests
import pandas as pd
import io
from sqlalchemy.orm import Session
from .database import engine
from .models import MetricCatalog, MetricRaw

WORLD_BANK_API_URL = "http://api.worldbank.org/v2/country/all/indicator/{indicator_id}?format=json&date={start_year}:{end_year}&per_page=10000"

def fetch_world_bank_data(start_year: int = 2000, end_year: int = 2023):
    """Fetches data from the World Bank API for relevant metrics and stores it in metrics_raw."""
    with Session(engine) as session:
        # Get World Bank metrics from the catalog
        wb_metrics = session.query(MetricCatalog).filter(MetricCatalog.source == "World Bank").all()

        if not wb_metrics:
            print("No World Bank metrics found in the catalog.")
            return

        all_raw_data = []

        for metric in wb_metrics:
            print(f"Fetching data for {metric.metric_id} ({metric.name})...")
            url = WORLD_BANK_API_URL.format(
                indicator_id=metric.metric_id,
                start_year=start_year,
                end_year=end_year
            )
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and len(data) > 1 and data[1] is not None:
                for entry in data[1]:
                    if entry['value'] is not None:
                        all_raw_data.append({
                            'country_code': entry['country']['id'],
                            'year': int(entry['date']),
                            'metric_id': metric.metric_id,
                            'metric_value': float(entry['value']),
                            'units': metric.units, # Use units from catalog
                            'source': metric.source
                        })
            else:
                print(f"No data or error for {metric.metric_id}: {data}")
        
        if all_raw_data:
            df_raw = pd.DataFrame(all_raw_data)
            # Handle potential duplicates before inserting
            df_raw.drop_duplicates(subset=['country_code', 'year', 'metric_id'], inplace=True)

            # Bulk insert into metrics_raw
            # Convert DataFrame to list of dictionaries for bulk_insert_mappings
            raw_data_to_insert = df_raw.to_dict(orient="records")
            session.bulk_insert_mappings(MetricRaw, raw_data_to_insert)
            session.commit()
            print(f"Successfully inserted {len(raw_data_to_insert)} raw data points from World Bank into metrics_raw.")
        else:
            print("No raw data from World Bank to insert.")


FAOSTAT_API_URL = "http://nsi-release-ro-statsuite.fao.org/rest/v2"

def fetch_faostat_v2_data(start_year: int = 2000, end_year: int = 2023):
    """Fetches data from the FAOSTAT V1 REST API for relevant metrics and stores it in metrics_raw."""
    with Session(engine) as session:
        faostat_metrics = session.query(MetricCatalog).filter(MetricCatalog.source == "FAOSTAT (V1)").all()

        if not faostat_metrics:
            print("No FAOSTAT (V1) metrics found in the catalog.")
            return

        all_raw_data = []

        for metric in faostat_metrics:
            print(f"Fetching data for {metric.metric_id} ({metric.name})...")
            # metric_id is like FAOSTAT_FS_21004_6120 (Dataset_Item_Element)
            parts = metric.metric_id.split('_')
            database_name = parts[1] # FS
            item_code = parts[2] # 21004
            element_code = parts[3] # 6120

            url = FAOSTAT_API_URL.format(
                database_name=database_name,
                elements=element_code,
                items=item_code,
                years=f"{start_year}:{end_year}"
            )
            response = requests.get(url)

            if response.status_code == 200 and response.text:
                try:
                    # Read CSV directly into a pandas DataFrame
                    df_faostat = pd.read_csv(io.StringIO(response.text))

                    # Map FAOSTAT column names to our schema
                    # This mapping might need adjustment based on actual CSV columns
                    for _, row in df_faostat.iterrows():
                        if pd.notna(row['Value']):
                            all_raw_data.append({
                                'country_code': row['Area Code'], # FAOSTAT numerical code
                                'year': int(row['Year']),
                                'metric_id': metric.metric_id,
                                'metric_value': float(row['Value']),
                                'units': row['Unit'],
                                'source': metric.source
                            })
                except Exception as e:
                    print(f"Error parsing FAOSTAT CSV data for {metric.metric_id}: {e}")
                    print(f"Response text: {response.text[:500]}...")
            else:
                print(f"No data or error for {metric.metric_id}: {response.status_code} - {response.text[:100]}...")
        
        if all_raw_data:
            df_raw = pd.DataFrame(all_raw_data)
            df_raw.drop_duplicates(subset=['country_code', 'year', 'metric_id'], inplace=True)
            raw_data_to_insert = df_raw.to_dict(orient="records")
            session.bulk_insert_mappings(MetricRaw, raw_data_to_insert)
            session.commit()
            print(f"Successfully inserted {len(raw_data_to_insert)} raw data points from FAOSTAT (V1) into metrics_raw.")
        else:
            print("No raw data from FAOSTAT (V1) to insert.")


def fetch_data(start_year: int = 2000, end_year: int = 2023):
    """Orchestrates fetching data from all configured sources."""
    with Session(engine) as session:
        print("Clearing existing raw metrics data...")
        session.query(MetricRaw).delete()
        session.commit()

    print("--- Fetching World Bank Data ---")
    fetch_world_bank_data(start_year, end_year)
    print("\n--- Fetching FAOSTAT (V2) Data ---")
    fetch_faostat_v2_data(start_year, end_year)
    print("\n--- Fetching WHO GHO Data ---")
    fetch_who_gho_data(start_year, end_year)

WHO_GHO_API_URL = "https://ghoapi.azureedge.net/api/{indicator_code}"

def fetch_who_gho_data(start_year: int = 2000, end_year: int = 2023):
    """Fetches data from the WHO GHO OData API for relevant metrics and stores it in metrics_raw."""
    with Session(engine) as session:
        who_gho_metrics = session.query(MetricCatalog).filter(MetricCatalog.source == "WHO GHO").all()

        if not who_gho_metrics:
            print("No WHO GHO metrics found in the catalog.")
            return

        all_raw_data = []

        for metric in who_gho_metrics:
            print(f"Fetching data for {metric.metric_id} ({metric.name})...")
            url = WHO_GHO_API_URL.format(indicator_code=metric.metric_id)
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and data and 'value' in data:
                for entry in data['value']:
                    # Filter by year range
                    if 'TimeDim' in entry and int(entry['TimeDim']) >= start_year and int(entry['TimeDim']) <= end_year:
                        if 'NumericValue' in entry and entry['NumericValue'] is not None:
                            all_raw_data.append({
                                'country_code': entry['SpatialDim'], # ISO3 code
                                'year': int(entry['TimeDim']),
                                'metric_id': metric.metric_id,
                                'metric_value': float(entry['NumericValue']),
                                'units': metric.units, # Use units from catalog
                                'source': metric.source
                            })
            else:
                print(f"No data or error for {metric.metric_id}: {data}")
        
        if all_raw_data:
            df_raw = pd.DataFrame(all_raw_data)
            df_raw.drop_duplicates(subset=['country_code', 'year', 'metric_id'], inplace=True)
            raw_data_to_insert = df_raw.to_dict(orient="records")
            session.bulk_insert_mappings(MetricRaw, raw_data_to_insert)
            session.commit()
            print(f"Successfully inserted {len(raw_data_to_insert)} raw data points from WHO GHO into metrics_raw.")
        else:
            print("No raw data from WHO GHO to insert.")


def fetch_who_gho_indicator_list():
    url = "https://ghoapi.azureedge.net/api/Indicator"
    response = requests.get(url)
    if response.status_code == 200:
        indicators = response.json()['value']
        for indicator in indicators:
            print(f"ID: {indicator['IndicatorCode']}, Title: {indicator['IndicatorName']}")
    else:
        print(f"Error fetching WHO GHO indicator list: {response.status_code}")


if __name__ == "__main__":
    # fetch_data()
    fetch_who_gho_indicator_list()