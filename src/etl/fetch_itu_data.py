
import os
import requests
import psycopg2
import psycopg2.extras
import pandas as pd
import io
from datetime import datetime

# ==============================================================================
# Configuration
# ==============================================================================

# Years to fetch data for
START_YEAR = 2019
END_YEAR = 2023

# ITU API endpoint base
ITU_API_BASE_URL = "https://api.datahub.itu.int/v2"

# List of ITU metrics to fetch
ITU_METRICS = [
    # Communications - Autonomy: International bandwidth usage
    {
        "metric_id": "ITU_INT_BANDWIDTH_USAGE",
        "name": "International bandwidth usage",
        "industry": "Communications",
        "pillar": "Autonomy",
        "directionality": "POS", # Higher usage is generally better
        "units": "Gbit/s", # Assuming this unit, will verify from data
        "source_url": "https://datahub.itu.int/",
        "itu_params": {
            "codeID": "242",
            "isCollection": "false",
        }
    },
    # Communications - Resilience: Mobile-broadband network coverage
    {
        "metric_id": "ITU_MOB_BB_COVERAGE",
        "name": "Population coverage, by mobile network technology",
        "industry": "Communications",
        "pillar": "Resilience",
        "directionality": "POS", # Higher coverage is better
        "units": "%", # Assuming this unit, will verify from data
        "source_url": "https://datahub.itu.int/",
        "itu_params": {
            "codeID": "100095",
            "isCollection": "true",
        }
    },
    # Information Technology - Resilience: Global Cybersecurity Index
    {
        "metric_id": "ITU_GCI",
        "name": "Global Cybersecurity Index",
        "industry": "Information Technology",
        "pillar": "Resilience",
        "directionality": "POS",
        "units": "Score",
        "source_url": "https://www.itu.int/en/ITU-D/Cybersecurity/Pages/gci.aspx",
        "itu_params": {
            "codeID": "100103",
            "isCollection": "false",
        }
    },
]

# ==============================================================================
# Database Functions (reused from World Bank script)
# ==============================================================================

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("CIVI_DB_HOST", "localhost"),
            port=os.environ.get("CIVI_DB_PORT", "5432"),
            dbname=os.environ.get("CIVI_DB_NAME", "civi"),
            user=os.environ.get("CIVI_DB_USER", "postgres"),
            password=os.environ.get("CIVI_DB_PASSWORD", "postgres")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 FATAL: Could not connect to PostgreSQL database.")
        print(f"   Please ensure the database is running and the following environment variables are set correctly:")
        print(f"   CIVI_DB_HOST, CIVI_DB_PORT, CIVI_DB_NAME, CIVI_DB_USER, CIVI_DB_PASSWORD")
        print(f"   Error: {e}")
        return None

def populate_catalog(conn):
    """Populates the metrics_catalog table with ITU metrics."""
    print("\n--- Populating Metrics Catalog for ITU ---")
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cur:
        for metric in ITU_METRICS:
            metric_id = metric["metric_id"]
            name = metric["name"]
            industry = metric["industry"]
            pillar = metric["pillar"]
            directionality = metric["directionality"]
            units = metric["units"]
            source_url = metric["source_url"]

            cur.execute(
                """
                INSERT INTO metrics_catalog (metric_id, name, industry, pillar, directionality, units, source, source_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO NOTHING;
                """,
                (metric_id, name, industry, pillar, directionality, units, "ITU", source_url, name)
            )
            if cur.rowcount > 0:
                inserted_count += 1
                print(f"  + Added '{metric_id}' to catalog.")
            else:
                skipped_count += 1
        conn.commit()
    print(f"\n✅ Catalog population complete. Added: {inserted_count}, Skipped (already exist): {skipped_count}")

def insert_raw_data(conn, data, metric_id):
    """Inserts a batch of raw metric data into the metrics_raw table."""
    if not data:
        return 0
    
    with conn.cursor() as cur:
        records_to_insert = []
        for record in data:
            # ITU data structure might be different. Assuming 'Country', 'Year', 'Value'
            country_code = record.get("Country ISO3") or record.get("Country Code") or record.get("Country")
            year_str = record.get("Year")
            value_str = record.get("Value")

            if country_code and year_str and value_str is not None:
                # --- Handle Year Parsing ---
                parsed_year = None
                if isinstance(year_str, str) and '-' in year_str:
                    try:
                        start_y, end_y = map(int, year_str.split('-'))
                        parsed_year = start_y 
                    except ValueError:
                        pass
                elif isinstance(year_str, (int, str)):
                    try:
                        parsed_year = int(year_str)
                    except ValueError:
                        pass
                
                # --- Handle Value Parsing ---
                parsed_value = None
                if isinstance(value_str, str):
                    try:
                        parsed_value = float(value_str)
                    except ValueError:
                        print(f"    - Skipping record due to non-numeric value: {record}")
                        continue # Skip to the next record
                elif isinstance(value_str, (int, float)):
                    parsed_value = float(value_str)

                if parsed_year is not None and parsed_value is not None:
                    try:
                        records_to_insert.append((
                            str(country_code),
                            parsed_year,
                            metric_id,
                            parsed_value,
                            "ITU"
                        ))
                    except (ValueError, TypeError) as e:
                        print(f"    - Skipping record due to final data conversion error: {record} - {e}")
                else:
                    print(f"    - Skipping record due to unparseable year or value: {record}")

        if not records_to_insert:
            return 0

        psycopg2.extras.execute_batch(cur,
            """
            INSERT INTO metrics_raw (country_code, year, metric_id, metric_value, source)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (country_code, year, metric_id) 
            DO UPDATE SET metric_value = EXCLUDED.metric_value, fetched_at = CURRENT_TIMESTAMP;
            """,
            records_to_insert
        )
        conn.commit()
        return len(records_to_insert)

# ==============================================================================
# ITU API Functions
# ==============================================================================

def fetch_itu_data(itu_params, start_year, end_year):
    """Fetches data for a specific indicator from the ITU DataHub API."""
    code_id = itu_params["codeID"]

    url = f"{ITU_API_BASE_URL}/data/download"
    params = {
        "codesid": code_id,
        "startyear": start_year,
        "endyear": end_year,
        "preview": "true"  # Use preview=true to get the data
    }

    headers = {}
    itu_api_key = os.environ.get("ITU_API_KEY")
    if itu_api_key:
        headers["Authorization"] = f"Bearer {itu_api_key}"
    else:
        print("    - Warning: ITU_API_KEY environment variable not set. API requests might be unauthorized.")

    try:
        response = requests.get(url, params=params, headers=headers, timeout=180)
        response.raise_for_status()
        
        json_data = response.json()

        if not isinstance(json_data, list):
            print(f"    - Unexpected JSON format from ITU API for codeID={code_id}. Expected a list.")
            return None

        all_data = json_data
        
        records_to_insert = []
        for record in all_data:
            if record.get('answer') and isinstance(record['answer'], list) and record['answer']:
                records_to_insert.append({
                    'Country ISO3': record.get('isoCode'),
                    'Year': record.get('dataYear'),
                    'Value': record['answer'][0].get('value')
                })

        if not records_to_insert:
            print(f"    - No data returned from ITU API for codeID={code_id} for {start_year}-{end_year}.")
            return None
        
        return records_to_insert
            
    except requests.exceptions.Timeout:
        print(f"    - Timeout fetching data for ITU codeID={code_id}. Request took longer than 180 seconds.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error fetching data for ITU codeID={code_id}: {e}")
        return None
    except ValueError: # Catches JSON decoding errors
        print(f"    - Error decoding JSON from ITU API for codeID={code_id}.")
        print(f"      Response text: {response.text[:500]}...") # Print first 500 chars
        return None
    except Exception as e:
        print(f"    - An unexpected error occurred while fetching/parsing ITU data for codeID={code_id}: {e}")
        return None
# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main function to run the ETL process for ITU data."""
    print("=================================================")
    print("  CIVI: ITU Data Ingestion Script")
    print("=================================================")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        # Step 1: Populate the metrics catalog
        populate_catalog(conn)

        # Step 2: Fetch and insert data for each metric
        print("\n--- Fetching Raw Data from ITU API ---")
        total_records_inserted = 0
        
        for metric in ITU_METRICS:
            metric_id = metric["metric_id"]
            print(f"\nFetching '{metric_id}'...")
            
            data = fetch_itu_data(metric["itu_params"], START_YEAR, END_YEAR)
            
            if data:
                inserted_count = insert_raw_data(conn, data, metric_id)
                print(f"  -> Inserted/Updated {inserted_count} records.")
                total_records_inserted += inserted_count
            else:
                print(f"  -> No data found for the period {START_YEAR}-{END_YEAR}.")

        print("\n=================================================")
        print("✅ ITU ETL process complete.")
        print(f"   Total records inserted/updated: {total_records_inserted}")
        print("=================================================")

    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    # Ensure required libraries are installed
    try:
        import requests
        import psycopg2
        import pandas as pd
    except ImportError:
        print("🔴 FATAL: Required Python libraries are not installed.")
        print("   Please install them by running: pip install requests psycopg2-binary pandas")
    else:
        main()
