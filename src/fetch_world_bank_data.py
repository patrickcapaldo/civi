
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
END_YEAR = 2024

# World Bank API endpoint
WB_API_URL = "http://api.worldbank.org/v2/country/all/indicator/{indicator}?date={start}:{end}&format=json&per_page=20000"

# List of World Bank metrics to fetch, based on the CIVI manifest
# Each entry: (metric_id, name, industry, pillar, directionality, units, source_url)
WORLD_BANK_METRICS = [
    # Communications
    ("IT.NET.BBND.P2", "Fixed-broadband subscriptions (per 100 people)", "Communications", "Sustainability", "POS", "%", "https://data.worldbank.org/indicator/IT.NET.BBND.P2"),
    ("IT.NET.USER.ZS", "Individuals using the Internet (% of population)", "Communications", "Effectiveness", "POS", "%", "https://data.worldbank.org/indicator/IT.NET.USER.ZS"),
    # Defence
    ("MS.MIL.XPND.GD.ZS", "Military expenditure (% of GDP)", "Defence", "Autonomy", "NEG", "% of GDP", "https://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS"),
    ("MS.MIL.TOTL.P1", "Armed forces personnel, total", "Defence", "Resilience", "POS", "Total", "https://data.worldbank.org/indicator/MS.MIL.TOTL.P1"),
    ("MS.MIL.XPND.ZS", "Military expenditure (% of central government expenditure)", "Defence", "Sustainability", "NEG", "% of govt. expenditure", "https://data.worldbank.org/indicator/MS.MIL.XPND.ZS"),
    # Energy
    ("EG.IMP.CONS.ZS", "Energy imports, net (% of energy use)", "Energy", "Autonomy", "NEG", "% of energy use", "https://data.worldbank.org/indicator/EG.IMP.CONS.ZS"),
    ("EG.ELC.LOSS.ZS", "Electric power transmission and distribution losses (% of output)", "Energy", "Resilience", "NEG", "% of output", "https://data.worldbank.org/indicator/EG.ELC.LOSS.ZS"),
    ("EG.FEC.RNEW.ZS", "Renewable energy consumption (% of total final energy consumption)", "Energy", "Sustainability", "POS", "%", "https://data.worldbank.org/indicator/EG.FEC.RNEW.ZS"),
    ("EG.ELC.ACCS.ZS", "Access to electricity (% of population)", "Energy", "Effectiveness", "POS", "%", "https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS"),
    # Finance
    ("FS.AST.PRVT.GD.ZS", "Domestic credit to private sector (% of GDP)", "Finance", "Autonomy", "POS", "% of GDP", "https://data.worldbank.org/indicator/FS.AST.PRVT.GD.ZS"),
    ("FB.AST.NPER.ZS", "Bank nonperforming loans to total gross loans (%)", "Finance", "Resilience", "NEG", "%", "https://data.worldbank.org/indicator/FB.AST.NPER.ZS"),
    ("FX.OWN.TOTL.ZS", "Account ownership at a financial institution or with a mobile-money-service provider (% of population ages 15+)", "Finance", "Sustainability", "POS", "%", "https://data.worldbank.org/indicator/FX.OWN.TOTL.ZS"),
    ("FB.CBK.BRCH.P5", "Commercial bank branches (per 100,000 adults)", "Finance", "Effectiveness", "POS", "Per 100,000 adults", "https://data.worldbank.org/indicator/FB.CBK.BRCH.P5"),
    # Healthcare
    ("SH.XPD.CHEX.PC.CD", "Current health expenditure per capita (current US$)", "Healthcare", "Sustainability", "POS", "Current US$", "https://data.worldbank.org/indicator/SH.XPD.CHEX.PC.CD"),
    ("SH.IMM.IDPT", "Immunization, DPT (% of children ages 12-23 months)", "Healthcare", "Effectiveness", "POS", "%", "https://data.worldbank.org/indicator/SH.IMM.IDPT"),
    # Transport
    ("IS.ROD.PAVE.ZS", "Paved roads (% of total roads)", "Transport", "Effectiveness", "POS", "% of total roads", "https://data.worldbank.org/indicator/IS.ROD.PAVE.ZS"),
    # Information Technology
    ("IT.NET.SECR.P6", "Secure Internet servers (per 1 million people)", "Information Technology", "Effectiveness", "POS", "Per 1 million people", "https://data.worldbank.org/indicator/IT.NET.SECR.P6"),
    ("GB.XPD.RSDV.GD.ZS", "Research and development expenditure (% of GDP)", "Information Technology", "Sustainability", "POS", "% of GDP", "https://data.worldbank.org/indicator/GB.XPD.RSDV.GD.ZS"),
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
    """Populates the metrics_catalog table with World Bank metrics."""
    print("--- Populating Metrics Catalog for World Bank ---")
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cur:
        for metric in WORLD_BANK_METRICS:
            metric_id, name, industry, pillar, directionality, units, source_url = metric
            cur.execute(
                """
                INSERT INTO metrics_catalog (metric_id, name, industry, pillar, directionality, units, source, source_url, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (metric_id) DO NOTHING;
                """,
                (metric_id, name, industry, pillar, directionality, units, "World Bank", source_url, name)
            )
            if cur.rowcount > 0:
                inserted_count += 1
                print(f"  + Added '{metric_id}' to catalog.")
            else:
                skipped_count += 1
        conn.commit()
    print(f"✅ Catalog population complete. Added: {inserted_count}, Skipped (already exist): {skipped_count}")

def insert_raw_data(conn, data, metric_id):
    """Inserts a batch of raw metric data into the metrics_raw table."""
    if not data:
        return 0
    
    with conn.cursor() as cur:
        # Prepare data for batch insertion
        records_to_insert = []
        for record in data:
            # Skip records with no value or invalid country code
            if record.get("value") is not None and record.get("countryiso3code") and len(record["countryiso3code"]) == 3:
                records_to_insert.append((
                    record["countryiso3code"],
                    int(record["date"]),
                    metric_id,
                    float(record["value"]),
                    "World Bank"
                ))
        
        if not records_to_insert:
            return 0

        # Use execute_batch for efficient insertion
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
# World Bank API Functions
# ==============================================================================

def fetch_wb_data(indicator_code, start_year, end_year):
    """Fetches data for a specific indicator from the World Bank API."""
    url = WB_API_URL.format(indicator=indicator_code, start=start_year, end=end_year)
    try:
        response = requests.get(url, timeout=180) # Increased timeout to 180 seconds
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        json_data = response.json()
        
        # The actual data is in the second element of the list
        if len(json_data) > 1 and json_data[1]:
            return json_data[1]
        else:
            # This can happen if the indicator has no data for the requested period
            print(f"    - No data returned from World Bank API for {indicator_code} for {start_year}-{end_year}.")
            return None
            
    except requests.exceptions.Timeout:
        print(f"    - Timeout fetching data for {indicator_code}. Request took longer than 180 seconds.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error fetching data for {indicator_code}: {e}")
        return None
    except (ValueError, IndexError):
        print(f"    - Error parsing JSON response for {indicator_code}.")
        return None

# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main function to run the ETL process for World Bank data."""
    print("=================================================")
    print("  CIVI: World Bank Data Ingestion Script")
    print("=================================================")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        # Step 1: Populate the metrics catalog
        populate_catalog(conn)

        # Step 2: Fetch and insert data for each metric
        print("--- Fetching Raw Data from World Bank API ---")
        total_records_inserted = 0
        
        for metric in WORLD_BANK_METRICS:
            metric_id = metric[0]
            print(f"Fetching '{metric_id}'...")
            
            data = fetch_wb_data(metric_id, START_YEAR, END_YEAR)
            
            if data:
                inserted_count = insert_raw_data(conn, data, metric_id)
                print(f"  -> Inserted/Updated {inserted_count} records.")
                total_records_inserted += inserted_count
            else:
                print(f"  -> No data found for the period {START_YEAR}-{END_YEAR}.")

        print(f"=================================================")
        print(f"✅ World Bank ETL process complete.")
        print(f"   Total records inserted/updated: {total_records_inserted}")
        print("=================================================")

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    # Ensure required libraries are installed
    try:
        import requests
        import psycopg2
    except ImportError:
        print("🔴 FATAL: Required Python libraries are not installed.")
        print("   Please install them by running: pip install requests psycopg2-binary")
    else:
        main()
