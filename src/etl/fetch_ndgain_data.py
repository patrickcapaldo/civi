
import os
import requests
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime

# ==============================================================================
# Configuration
# ==============================================================================

# ND-GAIN URL
NDGAIN_URL = "https://gain.nd.edu/assets/52018/nd_gain_country_index.csv"

# List of ND-GAIN metrics to fetch
NDGAIN_METRICS = [
    {
        "metric_id": "NDGAIN_SCORE",
        "name": "ND-GAIN Index",
        "industry": "Emergency Services",
        "pillar": "Resilience",
        "directionality": "POS",
        "units": "Score",
        "source_url": "https://gain.nd.edu/our-work/country-index/",
        "ndgain_column": "ND-GAIN Score"
    },
    {
        "metric_id": "NDGAIN_VULNERABILITY",
        "name": "ND-GAIN Vulnerability Score",
        "industry": "Emergency Services",
        "pillar": "Resilience",
        "directionality": "NEG",
        "units": "Score",
        "source_url": "https://gain.nd.edu/our-work/country-index/",
        "ndgain_column": "Vulnerability"
    },
    {
        "metric_id": "NDGAIN_READINESS",
        "name": "ND-GAIN Readiness Score",
        "industry": "Emergency Services",
        "pillar": "Resilience",
        "directionality": "POS",
        "units": "Score",
        "source_url": "https://gain.nd.edu/our-work/country-index/",
        "ndgain_column": "Readiness"
    }
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
    """Populates the metrics_catalog table with ND-GAIN metrics."""
    print("--- Populating Metrics Catalog for ND-GAIN ---")
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cur:
        for metric in NDGAIN_METRICS:
            cur.execute(
                """
                INSERT INTO metrics_catalog (metric_id, name, industry, pillar, directionality, units, source, source_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO NOTHING;
                """,
                (metric["metric_id"], metric["name"], metric["industry"], metric["pillar"], metric["directionality"], metric["units"], "ND-GAIN", metric["source_url"], metric["name"])
            )
            if cur.rowcount > 0:
                inserted_count += 1
                print(f"  + Added '{metric['name']}' to catalog.")
            else:
                skipped_count += 1
        conn.commit()
    print(f"✅ Catalog population complete. Added: {inserted_count}, Skipped (already exist): {skipped_count}")

def insert_raw_data(conn, data):
    """Inserts a batch of raw metric data into the metrics_raw table."""
    if data.empty:
        return 0
    
    total_inserted = 0
    with conn.cursor() as cur:
        for metric in NDGAIN_METRICS:
            records_to_insert = []
            metric_id = metric["metric_id"]
            column_name = metric["ndgain_column"]
            for index, row in data.iterrows():
                if pd.notna(row["ISO3"]) and pd.notna(row[column_name]) and pd.notna(row["Year"]):
                    records_to_insert.append((
                        row["ISO3"],
                        int(row["Year"]),
                        metric_id,
                        float(row[column_name]),
                        "ND-GAIN"
                    ))
            
            if not records_to_insert:
                continue

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
            total_inserted += len(records_to_insert)
            print(f"  -> Inserted/Updated {len(records_to_insert)} records for {metric_id}.")
    return total_inserted

# ==============================================================================
# ND-GAIN Functions
# ==============================================================================

def fetch_ndgain_data():
    """Fetches data from the ND-GAIN CSV file."""
    try:
        df = pd.read_csv(NDGAIN_URL)
        return df
    except Exception as e:
        print(f"    - Error fetching or parsing ND-GAIN data: {e}")
        return None

# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main function to run the ETL process for ND-GAIN data."""
    print("=================================================")
    print("  CIVI: ND-GAIN Data Ingestion Script")
    print("=================================================")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        populate_catalog(conn)

        print("--- Fetching Raw Data from ND-GAIN ---")
        
        data = fetch_ndgain_data()
        
        if data is not None:
            total_records_inserted = insert_raw_data(conn, data)
            print(f"=================================================")
            print(f"✅ ND-GAIN ETL process complete.")
            print(f"   Total records inserted/updated: {total_records_inserted}")
            print("=================================================")
        else:
            print("  -> No data found.")

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        import requests
        import psycopg2
        import pandas
    except ImportError:
        print("🔴 FATAL: Required Python libraries are not installed.")
        print("   Please install them by running: pip install requests psycopg2-binary pandas")
    else:
        main()
