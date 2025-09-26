
import os
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime

# ==============================================================================
# Configuration
# ==============================================================================

# Years to fetch data for
START_YEAR = 2019
END_YEAR = 2023

# WHO GHO API endpoint
WHO_GHO_API_URL = "https://ghoapi.azureedge.net/api/{indicator_code}"

# List of WHO metrics to fetch
WHO_METRICS = [
    # Healthcare
    ("HWF_0001", "Physicians per 1,000 population", "Healthcare", "Autonomy", "POS", "Per 1,000 population", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/physicians-density-(per-1000-population)"),
    ("UHC_INDEX_REPORTED", "UHC Service Coverage Index", "Healthcare", "Resilience", "POS", "Index (0-100)", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/uhc-service-coverage-index"),
    # Water
    ("WSH_WATER_SAFELY_MANAGED", "Population with access to safely managed drinking water (%)", "Water", "Resilience", "POS", "%", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/safely-managed-drinking-water-services-(sdg-6-1-1)"),
    ("WSH_SANITATION_SAFELY_MANAGED", "Population with access to safely managed sanitation services (%)", "Water", "Effectiveness", "POS", "%", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/safely-managed-sanitation-services-(sdg-6-2-1a)"),
    ("WHOSIS_000002", "Healthy life expectancy (HALE) at birth (years)", "Healthcare", "Effectiveness", "POS", "Years", "https://www.who.int/data/gho/data/indicators/indicator-details/GHO/healthy-life-expectancy-(hale)-at-birth-(years)"),
]

# ==============================================================================
# Database Functions
# ==============================================================================

def get_db_connection():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("CIVI_DB_HOST", "localhost"),
            port=os.environ.get("CIVI_DB_PORT", "5432"),
            dbname=os.environ.get("CIVI_DB_NAME", "civi"),
            user=os.environ.get("CIVI_DB_USER", "postgres"),
            <password>=os.environ.get("CIVI_DB_PASSWORD", "postgres")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 FATAL: Could not connect to PostgreSQL database.")
        print(f"   Please ensure the database is running and the following environment variables are set correctly:")
        print(f"   CIVI_DB_HOST, CIVI_DB_PORT, CIVI_DB_NAME, CIVI_DB_USER, CIVI_DB_PASSWORD")
        print(f"   Error: {e}")
        return None

def populate_catalog(conn):
    """Populates the metrics_catalog table with WHO metrics."""
    print("--- Populating Metrics Catalog for WHO ---")
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cur:
        for metric in WHO_METRICS:
            metric_id, name, industry, pillar, directionality, units, source_url = metric
            cur.execute(
                """
                INSERT INTO metrics_catalog (metric_id, name, industry, pillar, directionality, units, source, source_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO NOTHING;
                """,
                (metric_id, name, industry, pillar, directionality, units, "WHO", source_url, name)
            )
            if cur.rowcount > 0:
                inserted_count += 1
                print(f"  + Added '{name}' to catalog.")
            else:
                skipped_count += 1
        conn.commit()
    print(f"✅ Catalog population complete. Added: {inserted_count}, Skipped (already exist): {skipped_count}")

def insert_raw_data(conn, data, metric_id):
    """Inserts a batch of raw metric data into the metrics_raw table."""
    if not data:
        return 0
    
    with conn.cursor() as cur:
        records_to_insert = []
        for record in data:
            if record.get("SpatialDim") and record.get("TimeDim") and record.get("NumericValue") is not None:
                records_to_insert.append((
                    record["SpatialDim"],
                    int(record["TimeDim"]),
                    metric_id,
                    float(record["NumericValue"]),
                    "WHO"
                ))
        
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
# WHO API Functions
# ==============================================================================

def fetch_who_data(indicator_code, start_year, end_year):
    """Fetches data for a specific indicator from the WHO GHO API."""
    url = WHO_GHO_API_URL.format(indicator_code=indicator_code)
    filter_query = f"TimeDim ge {start_year} and TimeDim le {end_year}"
    params = {"$filter": filter_query}
    
    try:
        response = requests.get(url, params=params, timeout=180)
        response.raise_for_status()
        
        json_data = response.json()
        
        if "value" in json_data and json_data["value"]:
            return json_data["value"]
        else:
            print(f"    - No data returned from WHO API for {indicator_code} for {start_year}-{end_year}.")
            return None
            
    except requests.exceptions.Timeout:
        print(f"    - Timeout fetching data for {indicator_code}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error fetching data for {indicator_code}: {e}")
        return None
    except ValueError:
        print(f"    - Error parsing JSON response for {indicator_code}.")
        return None

# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main function to run the ETL process for WHO data."""
    print("=================================================")
    print("  CIVI: WHO Data Ingestion Script")
    print("=================================================")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        populate_catalog(conn)

        print("--- Fetching Raw Data from WHO GHO API ---")
        total_records_inserted = 0
        
        for metric in WHO_METRICS:
            metric_id = metric[0]
            print(f"Fetching '{metric[1]}'...")
            
            data = fetch_who_data(metric_id, START_YEAR, END_YEAR)
            
            if data:
                inserted_count = insert_raw_data(conn, data, metric_id)
                print(f"  -> Inserted/Updated {inserted_count} records.")
                total_records_inserted += inserted_count
            else:
                print(f"  -> No data found for the period {START_YEAR}-{END_YEAR}.")

        print(f"=================================================")
        print(f"✅ WHO ETL process complete.")
        print(f"   Total records inserted/updated: {total_records_inserted}")
        print("=================================================")

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        import requests
        import psycopg2
    except ImportError:
        print("🔴 FATAL: Required Python libraries are not installed.")
        print("   Please install them by running: pip install requests psycopg2-binary")
    else:
        main()
