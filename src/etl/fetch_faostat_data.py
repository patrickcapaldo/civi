
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

# FAOSTAT API endpoint base
FAOSTAT_API_BASE_URL = "https://faostatservices.fao.org/api/v1" # Updated base URL

# List of FAOSTAT metrics to fetch
# Each entry is a dictionary containing metric metadata and FAOSTAT-specific parameters
FAOSTAT_METRICS = [
    # Food & Agriculture - Autonomy: Cereal import dependency ratio
    {
        "metric_id": "FAO_FS_CIDR",
        "name": "Cereal import dependency ratio",
        "industry": "Food & Agriculture",
        "pillar": "Autonomy",
        "directionality": "NEG", # Higher dependency is worse for autonomy
        "units": "%",
        "source_url": "https://www.fao.org/faostat/en/#data/FS",
        "faostat_params": {
            "domain_code": "FS",
            "element_code": "6120", # Value (from Download URL)
            "item_code": "21035",   # Cereal import dependency ratio (percent) (3-year average) (from Download URL)
        }
    },
    # Food & Agriculture - Resilience: Cereal yield (kg per hectare)
    {
        "metric_id": "FAO_QCL_CEREAL_YIELD",
        "name": "Cereal yield (kg per hectare)",
        "industry": "Food & Agriculture",
        "pillar": "Resilience",
        "directionality": "POS", # Higher yield is better
        "units": "kg/Ha",
        "source_url": "https://www.fao.org/faostat/en/#data/QCL",
        "faostat_params": {
            "domain_code": "QCL",
            "element_code": "2413", # Yield (from Download URL)
            "item_code": "1717",   # Cereals, primary (from Download URL)
        }
    },
    # Food & Agriculture - Sustainability: Fertilizer consumption (Nutrient nitrogen N)
    {
        "metric_id": "FAO_RFB_FERT_N",
        "name": "Fertilizer consumption (Nutrient nitrogen N)",
        "industry": "Food & Agriculture",
        "pillar": "Sustainability",
        "directionality": "NEG", # High fertilizer use can be negative for sustainability
        "units": "tonnes", 
        "source_url": "https://www.fao.org/faostat/en/#data/RFN", # Updated domain in URL
        "faostat_params": {
            "domain_code": "RFN", # Corrected domain code
            "element_code": "2515", # Corrected element code for Agricultural Use
            "item_code": "3102",   # Nutrient nitrogen N
        }
    },
    # Food & Agriculture - Effectiveness: Food supply (kcal per capita per day)
    {
        "metric_id": "FAO_FBS_FOOD_SUPPLY_KCAL",
        "name": "Food supply (kcal per capita per day)",
        "industry": "Food & Agriculture",
        "pillar": "Effectiveness",
        "directionality": "POS", # Higher food supply is better
        "units": "kcal/capita/day",
        "source_url": "https://www.fao.org/faostat/en/#data/FBS",
        "faostat_params": {
            "domain_code": "FBS",
            "element_code": "664", # Food supply (kcal/capita/day)
            "item_code": "2901",   # Grand Total
        }
    },
    # Food & Agriculture - Effectiveness: Prevalence of undernourishment
    {
        "metric_id": "FAO_FS_UNDERNURISHMENT",
        "name": "Prevalence of undernourishment",
        "industry": "Food & Agriculture",
        "pillar": "Effectiveness",
        "directionality": "NEG", # Higher prevalence is worse
        "units": "%",
        "source_url": "https://www.fao.org/faostat/en/#data/FS",
        "faostat_params": {
            "domain_code": "FS",
            "element_code": "6120", # Value (assuming similar to CIDR)
            "item_code": "21004",   # Prevalence of undernourishment (percent) (from original)
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
    """Populates the metrics_catalog table with FAOSTAT metrics."""
    print("\n--- Populating Metrics Catalog for FAOSTAT ---")
    inserted_count = 0
    skipped_count = 0
    with conn.cursor() as cur:
        for metric in FAOSTAT_METRICS:
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
                (metric_id, name, industry, pillar, directionality, units, "FAOSTAT", source_url, name)
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
            country_code = record.get("Area Code (M49)")
            year_str = record.get("Year")
            value_str = record.get("Value")

            if country_code and year_str and value_str is not None:
                # --- Handle Year Parsing ---
                parsed_year = None
                if isinstance(year_str, str) and '-' in year_str:
                    # Handle year ranges like "2018-2020"
                    try:
                        start_y, end_y = map(int, year_str.split('-'))
                        parsed_year = start_y # Take the start year of the range
                    except ValueError:
                        pass # Will be caught by outer try-except
                elif isinstance(year_str, (int, str)):
                    try:
                        parsed_year = int(year_str)
                    except ValueError:
                        pass # Will be caught by outer try-except
                
                # --- Handle Value Parsing ---
                parsed_value = None
                if isinstance(value_str, str):
                    if value_str.startswith('<'):
                        try:
                            num = float(value_str[1:])
                            parsed_value = num - 0.1 # Approximate just below the threshold
                        except ValueError:
                            pass
                    elif value_str.startswith('>'):
                        try:
                            num = float(value_str[1:])
                            parsed_value = num + 0.1 # Approximate just above the threshold
                        except ValueError:
                            pass
                    else:
                        try:
                            parsed_value = float(value_str)
                        except ValueError:
                            pass
                elif isinstance(value_str, (int, float)):
                    parsed_value = float(value_str)

                if parsed_year is not None and parsed_value is not None:
                    try:
                        records_to_insert.append((
                            str(country_code),
                            parsed_year,
                            metric_id,
                            parsed_value,
                            "FAOSTAT"
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
# FAOSTAT API Functions
# ==============================================================================

def fetch_faostat_data(metric_params, start_year, end_year):
    """Fetches data for a specific indicator from the FAOSTAT API, handling pagination."""
    domain_code = metric_params["domain_code"]
    element_code = metric_params["element_code"]
    
    url = f"{FAOSTAT_API_BASE_URL}/en/data/{domain_code}"
    all_data = []
    page_number = 1
    page_size = 100 # Initial page size

    # Determine the item parameter name and value for logging
    item_param_name = "item"
    item_param_value = metric_params.get("item_code")

    while True:
        params = {
            "element": element_code,
            "year": ",".join(map(str, range(start_year, end_year + 1))),
            "area": "",
            "area_cs": "M49",
            "item_cs": "CPC",
            "format": "json",
            "show_codes": "true",
            "show_unit": "true",
            "show_flags": "true",
            "show_notes": "true",
            "null_values": "false",
            "caching": "false",
            "page_number": str(page_number),
            "page_size": str(page_size)
        }

        if "item_code" in metric_params:
            params["item"] = metric_params["item_code"]

        try:
            response = requests.get(url, params=params, timeout=180)
            response.raise_for_status()
            
            json_data = response.json()
            
            if json_data and "data" in json_data and json_data["data"]:
                current_page_data = json_data["data"]
                all_data.extend(current_page_data)
                
                if len(current_page_data) < page_size:
                    # Last page reached
                    break
                page_number += 1
            else:
                # No data on this page, or empty response
                if page_number == 1: # Only report "No data returned" if it's the first page
                    print(f"    - No data returned from FAOSTAT API for domain={domain_code}, element={element_code}, {item_param_name}={item_param_value} for {start_year}-{end_year}.")
                break # No more data or empty response
                
        except requests.exceptions.Timeout:
            print(f"    - Timeout fetching data for FAOSTAT domain={domain_code}, element={element_code}, {item_param_name}={item_param_value}. Request took longer than 180 seconds.")
            break
        except requests.exceptions.RequestException as e:
            print(f"    - Error fetching data for FAOSTAT domain={domain_code}, element={element_code}, {item_param_name}={item_param_value}: {e}")
            break
        except (ValueError, IndexError) as e:
            print(f"    - Error parsing JSON response for FAOSTAT domain={domain_code}, element={element_code}, {item_param_name}={item_param_value}: {e}")
            break
    
    return all_data if all_data else None

 # ==============================================================================                                         
 # Main Execution                                                                                                         
 # ==============================================================================                                         
                                                                                                                           
def main():                                                                                                              
    """Main function to run the ETL process for FAOSTAT data."""                                                         
    print("=================================================")                                                           
    print("  CIVI: FAOSTAT Data Ingestion Script")                                                                       
    print("=================================================")                                                           
                                                                                                                         
    conn = get_db_connection()                                                                                           
    if not conn:                                                                                                         
        return                                                                                                           
                                                                                                                          
    try:                                                                                                                 
        # Step 1: Populate the metrics catalog                                                                           
        populate_catalog(conn)                                                                                           
                                                                                                                          
        # Step 2: Fetch and insert data for each metric                                                                  
        print("\n--- Fetching Raw Data from FAOSTAT API ---")                                                            
        total_records_inserted = 0                                                                                       
                                                                                                                          
        for metric in FAOSTAT_METRICS:                                                                                   
            metric_id = metric["metric_id"]                                                                              
            print(f"\nFetching '{metric_id}'...")                                                                        
                                                                                                                          
            data = fetch_faostat_data(metric["faostat_params"], START_YEAR, END_YEAR)                                    
                                                                                                                          
            if data:                                                                                                     
                inserted_count = insert_raw_data(conn, data, metric_id)                                                  
                print(f"  -> Inserted/Updated {inserted_count} records.")                                                
                total_records_inserted += inserted_count                                                                 
            else:                                                                                                        
                print(f"  -> No data found for the period {START_YEAR}-{END_YEAR}.")                                     
                                                                                                                          
        print("\n=================================================")                                                     
        print("✅ FAOSTAT ETL process complete.")                                                                        
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
    except ImportError:                                                                                                  
        print("🔴 FATAL: Required Python libraries are not installed.")                                                  
        print("   Please install them by running: pip install requests psycopg2-binary")                                 
    else:                                                                                                                
        main()  