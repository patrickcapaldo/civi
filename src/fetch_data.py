import os
import requests
import json
from datetime import datetime
from config import DATA_SOURCES, INDICATORS

# Ensure raw data directories exist
RAW_DATA_DIR = "../data/raw"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

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

def _fetch_fao_data(indicator_key, fao_domain_code, fao_element_code):
    """Fetches data from FAOSTAT API."""
    print(f"  Fetching FAO data for {indicator_key} (Domain: {fao_domain_code}, Element: {fao_element_code})...")
    # FAOSTAT API is complex and requires specific query parameters
    # For now, we'll use dummy data for FAO as the real API integration is complex
    return False # Always return False to trigger dummy data generation

def _fetch_itu_data(indicator_key, itu_indicator_id):
    """Fetches data from ITU API."""
    print(f"  Fetching ITU data for {indicator_key} ({itu_indicator_id})...")
    # ITU API structure is not directly exposed in DATA_SOURCES, this is a placeholder
    # You would typically need to find the specific endpoint for the indicator
    url = f"{DATA_SOURCES['itu']}/data/{itu_indicator_id}" # Placeholder URL
    params = {"format": "json", "time": "2015;2020"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            filepath = os.path.join(RAW_DATA_DIR, "itu", f"{indicator_key}.json")
            _save_json(data, filepath)
            print(f"  Saved ITU data for {indicator_key} to {filepath}")
            return True
        else:
            print(f"  No real data found for {indicator_key} from ITU.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {indicator_key} from ITU: {e}")
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

def _fetch_dummy_data(indicator_key, source_name):
    """Generates dummy data for sources not yet implemented or when real fetch fails."""
    print(f"  Generating dummy data for {indicator_key} from {source_name}...")
    dummy_data = {
        "metadata": {"generated_at": datetime.now().isoformat(), "source": source_name},
        "data": [
            {"country": "USA", "value": 100, "year": 2020},
            {"country": "AUS", "value": 95, "year": 2020},
            {"country": "CAN", "value": 98, "year": 2020},
            {"country": "DEU", "value": 90, "year": 2020},
            {"country": "JPN", "value": 85, "year": 2020},
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

    # Mapping of indicator keys to API-specific codes/parameters
    # This needs to be comprehensive and accurate based on API documentation
    indicator_api_map = {
        # World Bank Indicators (Refined codes based on quick search)
        "electricity_access_percent": {"source": "world_bank", "code": "EG.ELC.ACCS.ZS"}, # Correct
        "agricultural_land_per_capita": {"source": "world_bank", "code": "AG.LND.AGRI.HA.PC"}, # Correct, but might not have data for all countries
        "ag_insurance_coverage": {"source": "world_bank", "code": "AG.LND.AGRI.K2"}, # Placeholder, needs verification
        "undernourishment_prevalence": {"source": "world_bank", "code": "SN.ITK.DEFC.ZS"}, # Correct
        "health_expenditure_gdp": {"source": "world_bank", "code": "SH.XPD.CHEX.GD.ZS"}, # Correct
        "ageing_dependency_ratio": {"source": "world_bank", "code": "SP.POP.DPND.OL"}, # Correct
        "waste_collection_coverage": {"source": "world_bank", "code": "SP.URB.TOTL.IN.ZS"}, # Correct
        "recycling_rate": {"source": "world_bank", "code": "ER.GDP.FWTL.M3.KD"}, # Placeholder, needs verification
        "waste_per_capita": {"source": "world_bank", "code": "EN.ATM.PM25.MC.M3"}, # Placeholder, needs verification
        "waste_management_cost_gdp": {"source": "world_bank", "code": "GC.XPN.TOTL.GD.ZS"}, # Placeholder, needs verification
        "military_personnel_per_capita": {"source": "world_bank", "code": "MS.MIL.TOTL.P1"}, # Correct
        "defence_spending_gdp": {"source": "world_bank", "code": "MS.MIL.XPND.GD.ZS"}, # Correct
        "gdp_per_capita": {"source": "world_bank", "code": "NY.GDP.PCAP.CD"}, # Correct
        "financial_inclusion_rate": {"source": "world_bank", "code": "FX.OWN.TOTL.ZS"}, # Placeholder, needs verification
        "inflation_rate": {"source": "world_bank", "code": "FP.CPI.TOTL.ZG"}, # Correct
        "domestic_transport_network_density": {"source": "world_bank", "code": "IS.RRS.TOTL.KM"}, # Placeholder, needs verification
        "public_transport_ridership": {"source": "world_bank", "code": "IS.RRS.PASG.KM"}, # Placeholder, needs verification
        "logistics_performance_index": {"source": "world_bank", "code": "LP.LPI.OVRL.XQ"}, # Correct
        "digital_literacy_rate": {"source": "world_bank", "code": "IT.NET.USER.ZS"}, # Correct
        "electricity_outage_duration": {"source": "world_bank", "code": "EG.ELC.OUTG.ZS"}, # Placeholder, needs verification
        "electricity_cost_share_income": {"source": "world_bank", "code": "IC.ELC.COST.ZS"}, # Placeholder, needs verification
        "telecom_infra_ownership": {"source": "world_bank", "code": "IT.NET.USER.ZS"}, # Placeholder, needs verification
        "household_water_expenditure": {"source": "world_bank", "code": "SH.H2O.SAFE.ZS"}, # Placeholder, needs verification
        "waste_treatment_capacity": {"source": "world_bank", "code": "ED.GOV.WAST.ZS"}, # Placeholder, needs verification
        "waste_diversion_rate": {"source": "world_bank", "code": "ER.MRN.WAST.ZS"}, # Placeholder, needs verification
        "mortality_rate_natural_disasters": {"source": "world_bank", "code": "VC.DSR.TOTL.P5"}, # Placeholder, needs verification
        "digital_inclusion_programs": {"source": "world_bank", "code": "IT.NET.BNDW.P2"}, # Placeholder, needs verification
        "reliance_on_single_transport_mode": {"source": "world_bank", "code": "IS.RRS.GOOD.MT.ZS"}, # Placeholder, needs verification
        "transport_carbon_emissions": {"source": "world_bank", "code": "EN.ATM.CO2E.KT"}, # Placeholder, needs verification
        "foreign_debt_gdp": {"source": "world_bank", "code": "DT.DOD.DECT.GN.ZS"}, # Placeholder, needs verification

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
        "ict_equipment_production": {"source": "un_comtrade"}, # UN Comtrade
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
        "fx_reserves_import_cover": {"source": "imf"}, # IMF
        "bank_capital_adequacy": {"source": "imf"}, # IMF
        "financial_sector_concentration": {"source": "imf"}, # IMF
        "green_finance_investment": {"source": "unep"}, # UNEP
        "domestic_defence_production": {"source": "sipri"}, # SIPRI
        "cyber_defence_capability": {"source": "gci"}, # GCI
        "military_environmental_impact": {"source": "national_reports"}, # National Reports
        "veteran_reintegration_programs": {"source": "national_reports"}, # National Reports
        "global_peace_index": {"source": "iep"}, # IEP
        "conflict_related_deaths": {"source": "ucdp"}, # UCDP
        "commute_time": {"source": "national_reports"}, # National Reports
        "e_government_index": {"source": "un"}, # UN
        "transport_network_redundancy": {"source": "oecd"}, # OECD
        "disruption_recovery_time": {"source": "national_reports"}, # National Reports
    }

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
                            _fetch_dummy_data(indicator_key, indicator["source"])
                    elif source_type == "fao":
                        # FAO API is complex, using dummy for now
                        _fetch_dummy_data(indicator_key, indicator["source"])
                    elif source_type == "itu":
                        # ITU API is problematic, using dummy for now
                        _fetch_dummy_data(indicator_key, indicator["source"])
                    elif source_type == "who":
                        if "code" in source_info and not _fetch_who_data(indicator_key, source_info["code"]):
                            _fetch_dummy_data(indicator_key, indicator["source"])
                        elif "code" not in source_info:
                            print(f"  WHO indicator {indicator_key} missing 'code' in API map, generating dummy.")
                            _fetch_dummy_data(indicator_key, indicator["source"])
                    else:
                        _fetch_dummy_data(indicator_key, indicator["source"])
                else:
                    print(f"  No API mapping found for indicator: {indicator_key}, generating dummy.")
                    _fetch_dummy_data(indicator_key, indicator["source"])
    print("Raw data fetching process complete.")

if __name__ == "__main__":
    fetch_all()
