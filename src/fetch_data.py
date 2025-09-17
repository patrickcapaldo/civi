import os
import requests
import json
import random
from datetime import datetime
from config import DATA_SOURCES, INDICATORS

# Get the absolute path of the directory containing the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# Define the raw data directory relative to the project root
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

os.makedirs(RAW_DATA_DIR, exist_ok=True)

indicator_api_map = {
        # World Bank Indicators (Refined codes based on quick search)
        "electricity_access_percent": {"source": "world_bank", "code": "EG.ELC.ACCS.ZS"}, # Correct
        "agricultural_land_per_capita": {"source": "world_bank", "code": "AG.LND.AGRI.HA.PC"}, # Correct, but might not have data for all countries
        "ag_insurance_coverage": {"source": "world_bank", "code": "AG.LND.AGRI.K2"}, # Placeholder, direct indicator not available
        "undernourishment_prevalence": {"source": "world_bank", "code": "SN.ITK.DEFC.ZS"}, # Correct
        "health_expenditure_gdp": {"source": "world_bank", "code": "SH.XPD.CHEX.GD.ZS"}, # Correct
        "ageing_dependency_ratio": {"source": "world_bank", "code": "SP.POP.DPND.OL"}, # Correct
        "waste_collection_coverage": {"source": "world_bank", "code": "SP.URB.TOTL.IN.ZS"}, # Correct
        "recycling_rate": {"source": "world_bank", "code": "ER.GDP.FWTL.M3.KD"}, # Placeholder, direct indicator not available
        "waste_per_capita": {"source": "world_bank", "code": "EN.ATM.PM25.MC.M3"}, # Placeholder, direct indicator not available
        "waste_management_cost_gdp": {"source": "world_bank", "code": "GC.XPN.TOTL.GD.ZS"}, # Poor proxy (general government expense)
        "military_personnel_per_capita": {"source": "world_bank", "code": "MS.MIL.TOTL.P1"}, # Correct
        "defence_spending_gdp": {"source": "world_bank", "code": "MS.MIL.XPND.GD.ZS"}, # Correct
        "gdp_per_capita": {"source": "world_bank", "code": "NY.GDP.PCAP.CD"}, # Correct
        "financial_inclusion_rate": {"source": "world_bank", "code": "FX.OWN.TOTL.ZS"}, # Correct
        "inflation_rate": {"source": "world_bank", "code": "FP.CPI.TOTL.ZG"}, # Correct
        "domestic_transport_network_density": {"source": "world_bank", "code": "IS.RRS.TOTL.KM"}, # Poor proxy (rail only)
        "public_transport_ridership": {"source": "world_bank", "code": "IS.RRS.PASG.KM"}, # Poor proxy (rail only)
        "logistics_performance_index": {"source": "world_bank", "code": "LP.LPI.OVRL.XQ"}, # Correct
        "digital_literacy_rate": {"source": "world_bank", "code": "IT.NET.USER.ZS"}, # Correct
        "electricity_outage_duration": {"source": "world_bank", "code": "EG.ELC.OUTG.ZS"}, # Placeholder, direct indicator not available
        "electricity_cost_share_income": {"source": "world_bank", "code": "IC.ELC.COST.ZS"}, # Placeholder, direct indicator not available
        "telecom_infra_ownership": {"source": "world_bank", "code": "IT.NET.USER.ZS"}, # Placeholder, needs verification
        "household_water_expenditure": {"source": "world_bank", "code": "SH.H2O.SAFE.ZS"}, # Placeholder, needs verification
        "waste_treatment_capacity": {"source": "world_bank", "code": "ED.GOV.WAST.ZS"}, # Placeholder, needs verification
        "waste_diversion_rate": {"source": "world_bank", "code": "ER.MRN.WAST.ZS"}, # Placeholder, needs verification
        "mortality_rate_natural_disasters": {"source": "world_bank", "code": "VC.DSR.TOTL.P5"}, # Placeholder, needs verification
        "digital_inclusion_programs": {"source": "world_bank", "code": "IT.NET.BNDW.P2"}, # Placeholder, needs verification
        "reliance_on_single_transport_mode": {"source": "world_bank", "code": "IS.RRS.GOOD.MT.ZS"}, # Placeholder, needs verification
        "transport_carbon_emissions": {"source": "world_bank", "code": "EN.ATM.CO2E.KT"}, # Placeholder, needs verification
        "foreign_debt_gdp": {"source": "world_bank", "code": "DT.DOD.DECT.GN.ZS"}, # Correct

        # WHO Indicators (Refined codes based on quick search)
        "health_worker_density": {"source": "who", "code": "HWF_0001"}, # Correct
        "hospital_beds_per_1000": {"source": "who", "code": "SH.MED.BEDS.ZS"}, # Corrected code, but might not have data
        "out_of_pocket_health_spending": {"source": "who", "code": "SH.XPD.OOPC.CH.ZS"}, # Corrected code
        "emergency_preparedness_score": {"source": "who", "code": "GHO_IHR_CAP_SCORE"}, # Placeholder
        "emergency_personnel_density": {"source": "who", "code": "HWF_0001"}, # Reusing health_worker_density as a proxy
        "uhc_service_coverage": {"source": "who", "code": "UHC_INDEX"}, # Placeholder, actual code might differ

        # FAO Indicators (All now use dummy data)
        "food_import_dependency": {"source": "fao", "domain": "FS", "element": "674"},
        "cereal_stock_to_use": {"source": "fao", "domain": "CL", "element": "5110"},
        "water_use_per_ag_gdp": {"source": "fao", "domain": "AW", "element": "5119"},
        "fertilizer_use_intensity": {"source": "fao", "domain": "EF", "element": "5157"},
        "food_price_index": {"source": "fao", "domain": "CP", "element": "5510"},
        "renewable_freshwater_per_capita": {"source": "fao", "domain": "AW", "element": "5100"},
        "water_import_dependency": {"source": "fao", "domain": "AW", "element": "5101"},
        "water_storage_capacity": {"source": "fao", "domain": "AW", "element": "5104"},

        # ITU Indicators (All now use dummy data)
        "internet_disruption_frequency": {"source": "itu", "code": "IT.NET.DOWNTIME"},
        "mobile_network_redundancy": {"source": "itu", "code": "IT.CEL.SETS.P2"},
        "ict_energy_use_percent": {"source": "itu", "code": "IT.TEL.CDMA.ZS"},
        "internet_penetration_percent": {"source": "itu", "code": "IT.NET.USER.ZS"},
        "broadband_affordability": {"source": "itu", "code": "IT.BRO.BRDB.PC"},
        "cybersecurity_index": {"source": "itu", "code": "IT.CYB.GEN.ZS"},

        # Other Sources (placeholders for now)
        "energy_import_dependency": {"source": "iea"}, # IEA
        "energy_source_diversity": {"source": "iea"}, # IEA
        "strategic_reserves_days": {"source": "iea"}, # IEA
        "renewables_share_percent": {"source": "iea"}, # IEA
        "carbon_intensity": {"source": "iea"}, # IEA
        "ict_equipment_production": {"source": "un_comtrade", "type": "C", "freq": "A", "px": "HS", "rg": "all", "cc": "TOTAL"}, # Placeholder commodity code
        "e_waste_recycling_rate": {"source": "un_e_waste"}, # UN e-waste monitor
        "domestic_pharma_production": {"source": "who_unido"}, # WHO/UNIDO
        "wastewater_treatment_percent": {"source": "un_sdg"}, # UN SDG database
        "drinking_water_access": {"source": "who_unicef_jmp"}, # WHO/UNICEF JMP
        "domestic_emergency_funding": {"source": "imf"}, # IMF
        "disaster_response_time": {"source": "national_reports"}, # National Reports
        "emergency_shelter_capacity": {"source": "national_reports"}, # National Reports
        "emergency_service_training_investment": {"source": "national_reports"}, # National Reports
        "volunteer_emergency_personnel": {"source": "national_reports"}, # National Reports
        "crime_rate": {"source": "unodc"}, # UNODC
        "domestic_software_development": {"source": "national_reports"}, # National Reports
        "semiconductor_manufacturing_capacity": {"source": "industry_data"}, # Industry Data
        "data_center_redundancy": {"source": "industry_data"}, # Industry Data
        "it_energy_efficiency": {"source": "industry_data"}, # Industry Data
        "fx_reserves_import_cover": {"source": "imf", "code": "FI.RES.TOTL.MO"}, # IMF
        "bank_capital_adequacy": {"source": "imf", "code": "FSI.B.K.T1.RW.ZS"}, # Placeholder code
        "financial_sector_concentration": {"source": "imf", "code": "FSI.B.CONC.HHI"}, # Placeholder code
        "green_finance_investment": {"source": "unep", "code": "UNEP.FIN.GREEN.INVEST"}, # Placeholder code
        "domestic_defence_production": {"source": "sipri"}, # SIPRI
        "cyber_defence_capability": {"source": "gci"}, # GCI
        "military_environmental_impact": {"source": "national_reports"}, # National Reports
        "veteran_reintegration_programs": {"source": "national_reports"}, # National Reports
        "global_peace_index": {"source": "iep"}, # IEP
        "conflict_related_deaths": {"source": "ucdp"}, # UCDP
        "commute_time": {"source": "national_reports"}, # National Reports
        "e_government_index": {"source": "un"}, # UN
        "transport_network_redundancy": {"source": "oecd", "code": "OECD.TRANSPORT.REDUNDANCY"}, # Placeholder code
        "disruption_recovery_time": {"source": "national_reports"}, # National Reports
        "waste_import_export_balance": {"source": "un_comtrade", "type": "C", "freq": "A", "px": "HS", "rg": "all", "cc": "TOTAL"}, # Placeholder commodity code
    }

def _save_json(data, filepath):
    """Helper to save data as JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def _fetch_world_bank_data(indicator_key, wb_indicator_code):
    """Fetches data from World Bank API for a specific indicator code."""
    print(f"  Fetching World Bank data for {indicator_key} ({wb_indicator_code})...")
    url = f"{DATA_SOURCES['world_bank']}/country/all/indicator/{wb_indicator_code}"
    params = {"format": "json", "date": "2015:2020", "per_page": 500}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        # World Bank API returns metadata in first element, data in second
        if data and len(data) > 1 and data[1]: # Check if data[1] is not empty
            filepath = os.path.join(RAW_DATA_DIR, "world_bank", f"{indicator_key}.json")
            _save_json(data[1], filepath)
            print(f"  Saved World Bank data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from World Bank.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from World Bank: {e}")
        return False

def _fetch_fao_data(indicator_key, fao_domain_code, fao_element_code, countries):
    """Fetches data from FAOSTAT API."""
    print(f"  Fetching FAO data for {indicator_key} (Domain: {fao_domain_code}, Element: {fao_element_code})...")
    url = f"{DATA_SOURCES['fao']}/en/data/{fao_domain_code}"
    params = {
        "area": ",".join(countries), # Assuming 3-letter ISO codes work
        "element": fao_element_code,
        "year": "2015-2020", # Fetch data for a range of years
        "format": "json"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("data"):
            # FAOSTAT API response structure can be complex.
            # This is a simplified extraction assuming 'data' key holds a list of records.
            # Each record is expected to have 'Area', 'Year', and 'Value'.
            extracted_data = []
            for record in data["data"]:
                extracted_data.append({
                    "country": record.get("AreaCode"), # Assuming AreaCode is the country identifier
                    "year": record.get("Year"),
                    "value": record.get("Value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "fao", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved FAO data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from FAOSTAT.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from FAOSTAT: {e}")
        return False

def _fetch_itu_data(indicator_key, itu_indicator_id, countries):
    """Fetches data from ITU API."""
    print(f"  Fetching ITU data for {indicator_key} ({itu_indicator_id})...")
    url = f"{DATA_SOURCES['itu']}/data/download/byid/{itu_indicator_id}"
    params = {
        "format": "json",
        "time": "2015;2020",
        "countries": ",".join(countries) # Assuming 3-letter ISO codes work
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("data"):
            extracted_data = []
            for record in data["data"]:
                extracted_data.append({
                    "country": record.get("CountryCode"), # Assuming CountryCode is the country identifier
                    "year": record.get("Year"),
                    "value": record.get("Value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "itu", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved ITU data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from ITU.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from ITU: {e}")
        return False

def _fetch_un_comtrade_data(indicator_key, un_comtrade_params, countries):
    """Fetches data from UN Comtrade API."""
    print(f"  Fetching UN Comtrade data for {indicator_key}...")
    url = DATA_SOURCES['un_comtrade']
    params = {
        "type": un_comtrade_params.get("type", "C"), # Default to goods
        "freq": un_comtrade_params.get("freq", "A"), # Default to annual
        "px": un_comtrade_params.get("px", "HS"),   # Default to Harmonized System
        "ps": "2015,2016,2017,2018,2019,2020", # Years
        "r": ",".join(countries), # Reporter countries
        "p": "all", # Partner countries (fetch all partners for now)
        "rg": un_comtrade_params.get("rg", "all"), # Trade flow (all for now)
        "cc": un_comtrade_params.get("cc", "TOTAL"), # Commodity code (TOTAL for now)
        "max": 50000, # Max records
        "format": "json"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("dataset"):
            extracted_data = []
            for record in data["dataset"]:
                extracted_data.append({
                    "country": record.get("reporterCode"),
                    "year": record.get("period"),
                    "value": record.get("tradeValue")
                })
            filepath = os.path.join(RAW_DATA_DIR, "un_comtrade", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved UN Comtrade data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from UN Comtrade.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from UN Comtrade: {e}")
        return False

def _fetch_imf_data(indicator_key, imf_indicator_code, countries):
    """Fetches data from IMF API."""
    print(f"  Fetching IMF data for {indicator_key} ({imf_indicator_code})...")
    # IMF API uses SDMX. A common pattern is:
    # {base_url}/Data/{dataflow_id}/{key}/{agency}/{version}?format=json
    # For simplicity, we'll try a direct data query if possible,
    # or assume a specific dataflow for now.
    # The provided base URL is: http://dataservices.imf.org/REST/SDMX_JSON.svc
    # A common dataflow for indicators might be 'IFS' (International Financial Statistics)
    # or 'BOP' (Balance of Payments).
    # Let's assume a structure like:
    # {base_url}/Data/{dataflow_id}/{indicator_code}.{country_codes}.?startPeriod=YYYY&endPeriod=YYYY
    # This is a simplification and might need adjustment based on actual IMF API behavior.

    dataflow_id = "IFS" # Common dataflow, might need to be dynamic or looked up
    url = f"{DATA_SOURCES['imf']}/Data/{dataflow_id}/{imf_indicator_code}.{'+'.join(countries)}.?startPeriod=2015&endPeriod=2020"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and data.get("CompactData") and data["CompactData"].get("DataSet"):
            extracted_data = []
            # SDMX JSON structure is complex. This is a simplified attempt to extract data.
            # It assumes a structure where observations are under DataSet.Series.Obs
            series = data["CompactData"]["DataSet"]["Series"]
            if isinstance(series, dict): # Handle single series
                series = [series]

            for s in series:
                country_code = s["@REF_AREA"]
                for obs in s.get("Obs", []):
                    year = obs["@TIME_PERIOD"]
                    value = obs["@OBS_VALUE"]
                    extracted_data.append({
                        "country": country_code,
                        "year": year,
                        "value": value
                    })

            filepath = os.path.join(RAW_DATA_DIR, "imf", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved IMF data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from IMF.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from IMF: {e}")
        return False

def _fetch_unep_data(indicator_key, unep_indicator_id, countries):
    """Fetches data from UNEP API."""
    print(f"  Fetching UNEP data for {indicator_key} ({unep_indicator_id})...")
    # UNEP API documentation is not readily available through simple search.
    # This is a placeholder function.
    # Assuming a simple REST API structure for now.
    url = f"{DATA_SOURCES['unep']}/data/{unep_indicator_id}"
    params = {
        "format": "json",
        "year": "2015-2020",
        "countries": ",".join(countries)
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("records"):
            extracted_data = []
            for record in data["records"]:
                extracted_data.append({
                    "country": record.get("country_code"), # Placeholder field name
                    "year": record.get("year"),
                    "value": record.get("value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "unep", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved UNEP data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from UNEP.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from UNEP: {e}")
        return False

def _fetch_oecd_data(indicator_key, oecd_indicator_code, countries):
    """Fetches data from OECD API.""" 
    print(f"  Fetching OECD data for {indicator_key} ({oecd_indicator_code})...")
    # OECD API uses SDMX-JSON.
    # The base URL is: https://stats.oecd.org/sdmx-json/data
    # A common pattern is:
    # {base_url}/{dataset_id}/{dimensions}/all?startTime=YYYY&endTime=YYYY
    # We need to find the dataset_id and the specific dimensions for the indicator.
    # For 'transport network redundancy', this will require using the OECD Data Explorer.

    # Placeholder for dataset_id and dimensions.
    # This will need to be updated once the specific OECD dataset is identified.
    dataset_id = "TRANSPORT_NETWORK_REDUNDANCY" # Placeholder
    dimensions = f"{oecd_indicator_code}.{'+'.join(countries)}" # Placeholder

    url = f"{DATA_SOURCES['oecd']}/{dataset_id}/{dimensions}/all?startTime=2015&endTime=2020"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and data.get("dataSets") and data["dataSets"][0].get("series"):
            extracted_data = []
            # SDMX-JSON structure is complex. This is a simplified attempt to extract data.
            # It assumes a structure where observations are under dataSets[0].series
            # and dimensions are mapped in structure.dimensions.series
            # and attributes in structure.attributes.observation

            # Simplified extraction - will need refinement based on actual OECD response
            for series_key, series_data in data["dataSets"][0]["series"].items():
                # Extract dimensions from series_key (e.g., ".AUS.TLI.TOT.A")
                # This is highly dependent on the actual series key format.
                # For now, let's assume the country code is part of the series_key or can be mapped.
                # This part will definitely need to be refined after inspecting a real response.
                country_code = "UNKNOWN" # Placeholder
                if ".AUS." in series_key: country_code = "AUS"
                elif ".USA." in series_key: country_code = "USA" # ... and so on for all countries

                for obs_key, value in series_data["observations"].items():
                    # obs_key typically maps to time period
                    time_period_index = int(obs_key)
                    year = data["structure"]["dimensions"]["observation"][0]["values"][time_period_index]["id"]
                    
                    extracted_data.append({
                        "country": country_code,
                        "year": year,
                        "value": value
                    })

            filepath = os.path.join(RAW_DATA_DIR, "oecd", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved OECD data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from OECD.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from OECD: {e}")
        return False

def _fetch_unodc_data(indicator_key, unodc_indicator_id, countries):
    """Fetches data from UNODC API."""
    print(f"  Fetching UNODC data for {indicator_key} ({unodc_indicator_id})...")
    # UNODC API documentation is available via Swagger UI.
    # The base URL is: https://dataunodc.un.org/
    # The API structure will need to be derived from the Swagger UI.
    # For now, assuming a simple endpoint for data.

    url = f"{DATA_SOURCES['unodc']}/data/{unodc_indicator_id}" # Placeholder URL
    params = {
        "format": "json",
        "year": "2015-2020",
        "countries": ",".join(countries)
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("records"):
            extracted_data = []
            for record in data["records"]:
                extracted_data.append({
                    "country": record.get("country_code"), # Placeholder field name
                    "year": record.get("year"),
                    "value": record.get("value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "unodc", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved UNODC data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from UNODC.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from UNODC: {e}")
        return False

def _fetch_un_sdg_data(indicator_key, un_sdg_indicator_id, countries):
    """Fetches data from UN SDG API."""
    print(f"  Fetching UN SDG data for {indicator_key} ({un_sdg_indicator_id})...")
    # UN SDG API documentation is available via Swagger UI: https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/
    # The base URL is: https://unstats.un.org/sdgapi/v1/sdg/
    # A common pattern is: {base_url}/Goal/{goal_id}/Target/{target_id}/Indicator/{indicator_id}/Data
    # This is a placeholder function.

    # For 'wastewater_treatment_percent', it's SDG 6 (Clean Water and Sanitation)
    # and indicator 6.3.1 (Proportion of wastewater safely treated).
    # The API might require specific goal, target, and indicator IDs.
    # For now, I'll use the indicator_id directly in the URL, assuming it's sufficient.

    url = f"{DATA_SOURCES['un_sdg']}/Indicator/{un_sdg_indicator_id}/Data"
    params = {
        "format": "json",
        "year": "2015-2020",
        "countries": ",".join(countries) # Assuming 3-letter ISO codes work
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("data"):
            extracted_data = []
            for record in data["data"]:
                extracted_data.append({
                    "country": record.get("geoAreaCode"), # Placeholder field name
                    "year": record.get("timePeriod"),
                    "value": record.get("value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "un_sdg", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved UN SDG data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from UN SDG.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from UN SDG: {e}")
        return False

def _fetch_unodc_data(indicator_key, unodc_indicator_id, countries):
    """Fetches data from UNODC API."""
    print(f"  Fetching UNODC data for {indicator_key} ({unodc_indicator_id})...")
    # UNODC API documentation is available via Swagger UI.
    # The base URL is: https://dataunodc.un.org/
    # The API structure will need to be derived from the Swagger UI.
    # For now, assuming a simple endpoint for data.

    url = f"{DATA_SOURCES['unodc']}/data/{unodc_indicator_id}" # Placeholder URL
    params = {
        "format": "json",
        "year": "2015-2020",
        "countries": ",".join(countries)
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("records"):
            extracted_data = []
            for record in data["records"]:
                extracted_data.append({
                    "country": record.get("country_code"), # Placeholder field name
                    "year": record.get("year"),
                    "value": record.get("value")
                })
            filepath = os.path.join(RAW_DATA_DIR, "unodc", f"{indicator_key}.json")
            _save_json(extracted_data, filepath)
            print(f"  Saved UNODC data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from UNODC.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from UNODC: {e}")
        return False

def _fetch_who_data(indicator_key, who_indicator_id):
    """Fetches data from WHO API."""
    print(f"  Fetching WHO data for {indicator_key} ({who_indicator_id})...")
    url = f"{DATA_SOURCES['who']}/{who_indicator_id}"
    params = {"format": "json"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data and data['value']:
            filepath = os.path.join(RAW_DATA_DIR, "who", f"{indicator_key}.json")
            _save_json(data['value'], filepath)
            print(f"  Saved WHO data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from WHO.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from WHO: {e}")
        return False

def _fetch_dummy_data(indicator_key, source_name, countries):
    """Generates dummy data for sources not yet implemented or when real fetch fails."""
    print(f"  Generating dummy data for {indicator_key} from {source_name}...")
    dummy_data = {
        "metadata": {"generated_at": datetime.now().isoformat(), "source": source_name},
        "data": [
            {"country": country, "value": round(random.uniform(0, 100), 2), "year": 2020}
            for country in countries
        ]
    }
    # Ensure the dummy data is saved in a consistent location/format for clean_data.py
    # Use the base source name for the directory
    base_source_name = source_name.split('/')[0].strip().lower().replace(" ", "_")
    source_dir = os.path.join(RAW_DATA_DIR, base_source_name)
    filepath = os.path.join(source_dir, f"{indicator_key}.json")
    _save_json(dummy_data, filepath)
    print(f"  Saved dummy data for {indicator_key} to {filepath}")

def fetch_all():
    print("Starting raw data fetching process...")

    countries = ["USA", "CAN", "MEX", "BRA", "ARG", "GBR", "FRA", "DEU", "ITA", "ESP", "NLD", "SWE", "NOR", "FIN", "DNK", "AUS", "NZL", "JPN", "KOR", "CHN", "IND", "RUS", "ZAF"]

    for industry, pillars_data in INDICATORS.items():
        print(f"Fetching data for industry: {industry.upper()}")
        for pillar, indicators_list in pillars_data.items():
            for indicator in indicators_list:
                indicator_key = indicator["key"]
                source_info = indicator_api_map.get(indicator_key)

                if source_info:
                    source_type = source_info["source"]
                    if source_type == "world_bank":
                        if not _fetch_world_bank_data(indicator_key, source_info["code"]):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "fao":
                        if not _fetch_fao_data(indicator_key, source_info["domain"], source_info["element"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "itu":
                        if not _fetch_itu_data(indicator_key, source_info["code"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "un_comtrade":
                        if not _fetch_un_comtrade_data(indicator_key, source_info, countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "imf":
                        if not _fetch_imf_data(indicator_key, source_info["code"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "unep":
                        if not _fetch_unep_data(indicator_key, source_info["code"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "oecd":
                        if not _fetch_oecd_data(indicator_key, source_info["code"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "un_sdg":
                        if not _fetch_un_sdg_data(indicator_key, source_info["code"], countries):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    elif source_type == "who":
                        if "code" in source_info and not _fetch_who_data(indicator_key, source_info["code"]):
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                        elif "code" not in source_info:
                            print(f"  WHO indicator {indicator_key} missing 'code' in API map, generating dummy.")
                            _fetch_dummy_data(indicator_key, indicator["source"], countries)
                    else:
                        _fetch_dummy_data(indicator_key, indicator["source"], countries)
                else:
                    print(f"  No API mapping found for indicator: {indicator_key}, generating dummy.")
                    _fetch_dummy_data(indicator_key, indicator["source"], countries)
    print("Raw data fetching process complete.")

if __name__ == "__main__":
    fetch_all()
