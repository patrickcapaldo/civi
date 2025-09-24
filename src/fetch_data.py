import requests
import pandas as pd
import xml.etree.ElementTree as ET
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


FAOSTAT_SDMX_API_URL = "https://nsi-release-ro-statsuite.fao.org/rest/data/FAO,{dataset_id},1.0/A.{indicator_id}..........?startPeriod={start_year}&endPeriod={end_year}&dimensionAtObservation=AllDimensions"

def fetch_faostat_sdmx_data(start_year: int = 2000, end_year: int = 2023):
    """Fetches data from the FAOSTAT SDMX API for relevant metrics and stores it in metrics_raw."""
    with Session(engine) as session:
        faostat_metrics = session.query(MetricCatalog).filter(MetricCatalog.source == "FAOSTAT (SDMX)").all()

        if not faostat_metrics:
            print("No FAOSTAT (SDMX) metrics found in the catalog.")
            return

        all_raw_data = []

        for metric in faostat_metrics:
            print(f"Fetching data for {metric.metric_id} ({metric.name})...")
            # metric_id is like FAOSTAT_SDG_2_1_1_SN_ITK_DEFC
            dataset_id = "DF_SDG_2_1_1" # Hardcode for now
            indicator_id = "SN_ITK_DEFC" # Hardcode for now
            url = FAOSTAT_SDMX_API_URL.format(
                dataset_id=dataset_id,
                indicator_id=indicator_id,
                start_year=start_year,
                end_year=end_year
            )
            response = requests.get(url)

            if response.status_code == 200 and response.text:
                try:
                    root = ET.fromstring(response.text)
                    # Define namespaces for easier parsing
                    namespaces = {
                        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
                        'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
                        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
                    }

                    # Find all Series elements
                    for series in root.findall('.//generic:Series', namespaces):
                        # Extract dimensions from SeriesKey
                        series_key_values = {kv.get('id'): kv.get('value') for kv in series.findall('.//generic:SeriesKey/generic:Value', namespaces)}
                        
                        # Extract observations within each series
                        for obs in series.findall('.//generic:Obs', namespaces):
                            # Extract attributes from generic:Attributes
                            attributes = {attr.get('id'): attr.get('value') for attr in obs.findall('.//generic:Attributes/generic:Value', namespaces)}

                            country_code = attributes.get('REF_AREA_ISO3')
                            time_detail = attributes.get('TIME_DETAIL')
                            value_element = obs.find('.//generic:ObsValue', namespaces)
                            value = value_element.get('value') if value_element is not None else None

                            if country_code and time_detail and value is not None:
                                # Extract the start year from the TIME_DETAIL range (e.g., "2022-2024" -> 2022)
                                year = int(time_detail.split('-')[0])

                                all_raw_data.append({
                                    'country_code': country_code,
                                    'year': year,
                                    'metric_id': metric.metric_id,
                                    'metric_value': float(value),
                                    'units': metric.units,
                                    'source': metric.source
                                })
                except ET.ParseError as e:
                    print(f"Error parsing FAOSTAT SDMX XML for {metric.metric_id}: {e}")
                    print(f"Response text: {response.text[:500]}...")
                except Exception as e:
                    print(f"Error processing FAOSTAT SDMX data for {metric.metric_id}: {e}")
                    print(f"Response text: {response.text[:500]}...")
            else:
                print(f"No data or error for {metric.metric_id}: {response.status_code} - {response.text[:100]}...")
        
        if all_raw_data:
            df_raw = pd.DataFrame(all_raw_data)
            df_raw.drop_duplicates(subset=['country_code', 'year', 'metric_id'], inplace=True)
            raw_data_to_insert = df_raw.to_dict(orient="records")
            session.bulk_insert_mappings(MetricRaw, raw_data_to_insert)
            session.commit()
            print(f"Successfully inserted {len(raw_data_to_insert)} raw data points from FAOSTAT (SDMX) into metrics_raw.")
        else:
            print("No raw data from FAOSTAT (SDMX) to insert.")



def fetch_data(start_year: int = 2000, end_year: int = 2023):
    """Orchestrates fetching data from all configured sources."""
    with Session(engine) as session:
        print("Clearing existing raw metrics data...")
        session.query(MetricRaw).delete()
        session.commit()

    print("--- Fetching World Bank Data ---")
    fetch_world_bank_data(start_year, end_year)
    # print("\n--- Fetching FAOSTAT (SDMX) Data ---")
    # fetch_faostat_sdmx_data(start_year, end_year)


if __name__ == "__main__":
    fetch_data()