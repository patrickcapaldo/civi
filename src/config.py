"""
Configuration file for CIVI (Critical Infrastructure Vitals Index).
Defines industries, pillars, indicators, weights, and data sources.
"""

from datetime import datetime

# -------------------------------------------------------------------
# Project Metadata
# -------------------------------------------------------------------
PROJECT_NAME = "Critical Infrastructure Vitals Index (CIVI)"
VERSION = "1.0"
LAST_UPDATED = datetime.utcnow().strftime("%Y-%m-%d")

# -------------------------------------------------------------------
# Pillars
# -------------------------------------------------------------------
PILLARS = ["autonomy", "resilience", "sustainability", "effectiveness"]

# -------------------------------------------------------------------
# Critical Industries
# -------------------------------------------------------------------
INDUSTRIES = [
    "communications",
    "defence",
    "energy",
    "finance",
    "food_agriculture",
    "healthcare",
    "transport",
    "water",
    "waste_management",
    "emergency_services",
    "information_technology",
]

# -------------------------------------------------------------------
# Indicators by Industry & Pillar
# Each indicator entry:
#   key: short name
#   description: human-readable explanation
#   source: dataset/provider
#   weight: relative importance within the pillar
#   higher_is_better: True if higher value is better, False if lower is better
# -------------------------------------------------------------------
INDICATORS = {
    "food_agriculture": {
        "autonomy": [
            {
                "key": "food_import_dependency",
                "description": "Food import dependency ratio (%)",
                "source": "FAO",
                "weight": 0.7,
                "higher_is_better": False,
            },
            {
                "key": "agricultural_land_per_capita",
                "description": "Hectares of agricultural land per capita",
                "source": "FAO/World Bank",
                "weight": 0.3,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "cereal_stock_to_use",
                "description": "Cereal stock-to-use ratio (%)",
                "source": "FAO",
                "weight": 0.6,
                "higher_is_better": True,
            },
            {
                "key": "ag_insurance_coverage",
                "description": "Agricultural insurance coverage (Direct indicator not available, placeholder used)",
                "source": "World Bank",
                "weight": 0.4,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "water_use_per_ag_gdp",
                "description": "Cubic meters of water per unit of agricultural GDP",
                "source": "FAO AQUASTAT",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "fertilizer_use_intensity",
                "description": "Fertilizer use (kg/ha)",
                "source": "FAO",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "effectiveness": [
            {
                "key": "undernourishment_prevalence",
                "description": "Share of population undernourished (%)",
                "source": "FAO/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "food_price_index",
                "description": "National food price index (normalized)",
                "source": "FAO",
                "weight": 0.5,
                "higher_is_better": False, # Assuming lower price index is better for stability
            },
        ],
    },

    "energy": {
        "autonomy": [
            {
                "key": "energy_import_dependency",
                "description": "Share of energy supply that is imported (%)",
                "source": "IEA/World Bank",
                "weight": 0.6,
                "higher_is_better": False,
            },
            {
                "key": "energy_source_diversity",
                "description": "Diversity index (HHI) of domestic energy sources",
                "source": "IEA",
                "weight": 0.4,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "electricity_outage_duration",
                "description": "Average annual outage duration (SAIDI - No direct WB indicator, placeholder used)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "strategic_reserves_days",
                "description": "Days of strategic fuel reserves available",
                "source": "IEA",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "renewables_share_percent",
                "description": "Share of renewables in total energy (%)",
                "source": "IEA",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "carbon_intensity",
                "description": "CO₂ emissions per kWh electricity (gCO2/kWh)",
                "source": "IEA",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "effectiveness": [
            {
                "key": "electricity_access_percent",
                "description": "Population with access to electricity (%)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "electricity_cost_share_income",
                "description": "Household electricity cost as % of income (No direct WB indicator, placeholder used)",
                "source": "OECD/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "communications": {
        "autonomy": [
            {
                "key": "telecom_infra_ownership",
                "description": "Domestic share of telecom infrastructure ownership (proxy: % state-owned vs foreign)",
                "source": "ITU/World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "ict_equipment_production",
                "description": "Domestic production of ICT equipment (proxy: ICT trade balance, UN Comtrade)",
                "source": "UN Comtrade",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "internet_disruption_frequency",
                "description": "Internet disruption frequency (downtime events per year)",
                "source": "ITU",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "mobile_network_redundancy",
                "description": "Mobile network redundancy (3G/4G/5G coverage overlap %)",
                "source": "ITU",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "ict_energy_use_percent",
                "description": "Energy use of ICT sector (as % national energy)",
                "source": "ITU",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "e_waste_recycling_rate",
                "description": "E-waste recycling rate (%)",
                "source": "UN e-waste monitor",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "internet_penetration_percent",
                "description": "Internet penetration (% of population)",
                "source": "ITU",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "broadband_affordability",
                "description": "Broadband affordability (% of GNI per capita)",
                "source": "ITU/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "healthcare": {
        "autonomy": [
            {
                "key": "domestic_pharma_production",
                "description": "Domestic pharmaceutical production (% of national consumption)",
                "source": "WHO/UNIDO",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "health_worker_density",
                "description": "Health worker density per 1,000",
                "source": "WHO",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "hospital_beds_per_1000",
                "description": "Surge capacity (hospital beds per 1,000)",
                "source": "WHO",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "emergency_preparedness_score",
                "description": "Emergency preparedness score (IHR Capacity Index)",
                "source": "WHO",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "health_expenditure_gdp",
                "description": "Health expenditure (% of GDP, public + private)",
                "source": "WHO/World Bank",
                "weight": 0.5,
                "higher_is_better": True, # Assuming higher expenditure indicates more sustainable investment
            },
            {
                "key": "ageing_dependency_ratio",
                "description": "Ageing dependency ratio (demographic pressure)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "effectiveness": [
            {
                "key": "uhc_service_coverage",
                "description": "Universal Health Coverage Index (UHC Service Coverage)",
                "source": "WHO",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "out_of_pocket_health_spending",
                "description": "Out-of-pocket health spending (% of total health expenditure)",
                "source": "WHO",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "water": {
        "autonomy": [
            {
                "key": "renewable_freshwater_per_capita",
                "description": "Renewable freshwater resources per capita",
                "source": "FAO AQUASTAT",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "water_import_dependency",
                "description": "Water import dependency (transboundary inflow as % of resources)",
                "source": "FAO",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "resilience": [
            {
                "key": "safely_managed_water_access",
                "description": "% population with access to safely managed water supply (short-term robustness)",
                "source": "WHO/UNICEF JMP",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "water_storage_capacity",
                "description": "Water storage capacity per capita (dams/reservoirs)",
                "source": "FAO",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "water_stress_index",
                "description": "Water stress index (% withdrawals of available resources)",
                "source": "FAO/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "wastewater_treatment_percent",
                "description": "Wastewater treatment (% safely treated)",
                "source": "UN SDG database",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "drinking_water_access",
                "description": "Access to safely managed drinking water (%)",
                "source": "WHO/UNICEF JMP",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "household_water_expenditure",
                "description": "Average household water expenditure (% income)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "waste_management": {
        "autonomy": [
            {
                "key": "waste_treatment_capacity",
                "description": "Domestic waste treatment capacity (tons/year per capita)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "waste_import_export_balance",
                "description": "Waste import/export balance (net tons per capita)",
                "source": "UN Comtrade",
                "weight": 0.5,
                "higher_is_better": False, # Assuming net export of waste is worse for autonomy
            },
        ],
        "resilience": [
            {
                "key": "landfill_lifespan",
                "description": "Remaining landfill lifespan (years)",
                "source": "National Reports/World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "waste_collection_coverage",
                "description": "Waste collection coverage (% of population)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "recycling_rate",
                "description": "Recycling rate (No direct WB indicator, placeholder used)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "waste_diversion_rate",
                "description": "Waste diversion rate (from landfill/incineration)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "waste_per_capita",
                "description": "Waste generation per capita (kg/day) (No direct WB indicator, placeholder used)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "waste_management_cost_gdp",
                "description": "Waste management cost (% of GDP) (General expense indicator used as proxy)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "emergency_services": {
        "autonomy": [
            {
                "key": "domestic_emergency_funding",
                "description": "Domestic funding for emergency services (% of total)",
                "source": "National Reports/IMF",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "emergency_personnel_density",
                "description": "Emergency personnel density (per 1,000 population)",
                "source": "WHO/National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "disaster_response_time",
                "description": "Average disaster response time (hours)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "emergency_shelter_capacity",
                "description": "Emergency shelter capacity (beds per 1,000 population)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "emergency_service_training_investment",
                "description": "Investment in emergency service training (% of budget)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "volunteer_emergency_personnel",
                "description": "Volunteer emergency personnel (% of total)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "mortality_rate_natural_disasters",
                "description": "Mortality rate from natural disasters (per 100,000)",
                "source": "World Bank/UNISDR",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "crime_rate",
                "description": "Crime rate (per 100,000 population)",
                "source": "UNODC/National Reports",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "information_technology": {
        "autonomy": [
            {
                "key": "domestic_software_development",
                "description": "Domestic software development (% of market share)",
                "source": "National Reports/Industry Data",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "semiconductor_manufacturing_capacity",
                "description": "Semiconductor manufacturing capacity (proxy: fab output)",
                "source": "Industry Data",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "cybersecurity_index",
                "description": "National Cybersecurity Index score",
                "source": "ITU/National Cybersecurity Agencies",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "data_center_redundancy",
                "description": "Data center redundancy (Tier III+ facilities as % of total)",
                "source": "Industry Data",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "it_energy_efficiency",
                "description": "IT energy efficiency (PUE for data centers)",
                "source": "Industry Data",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "digital_inclusion_programs",
                "description": "Digital inclusion programs (proxy: government spending)",
                "source": "World Bank/National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "digital_literacy_rate",
                "description": "Digital literacy rate (% of population)",
                "source": "ITU/World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "e_government_index",
                "description": "E-Government Development Index (EGDI)",
                "source": "UN",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
    },

    "finance": {
        "autonomy": [
            {
                "key": "foreign_debt_gdp",
                "description": "External debt stocks (% of GNI)",
                "source": "World Bank/IMF",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "fx_reserves_import_cover",
                "description": "Foreign exchange reserves (months of import cover) (IMF API connection issues, manual data required)",
                "source": "IMF",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "bank_capital_adequacy",
                "description": "Bank capital adequacy ratio (Tier 1) (IMF API connection issues, manual data required)",
                "source": "IMF/National Regulators",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "financial_sector_concentration",
                "description": "Financial sector concentration (HHI of top 5 banks) (IMF API connection issues, manual data required)",
                "source": "IMF",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "sustainability": [
            {
                "key": "green_finance_investment",
                "description": "Green finance investment (% of total investment) (UNEP API not investigated, manual data required)",
                "source": "UNEP/Industry Data",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "financial_inclusion_rate",
                "description": "Account ownership at a financial institution or with a mobile-money-service provider (% of population ages 15+)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "gdp_per_capita",
                "description": "GDP per capita (current US$)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "inflation_rate",
                "description": "Inflation rate (% annual)",
                "source": "World Bank/IMF",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "transport": {
        "autonomy": [
            {
                "key": "domestic_transport_network_density",
                "description": "Domestic transport network density (Rail lines only, km/sq km)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "reliance_on_single_transport_mode",
                "description": "Reliance on single transport mode (e.g., % freight by road)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "resilience": [
            {
                "key": "transport_network_redundancy",
                "description": "Transport network redundancy (alternative routes index)",
                "source": "OECD/National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "disruption_recovery_time",
                "description": "Average disruption recovery time (hours)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "sustainability": [
            {
                "key": "public_transport_ridership",
                "description": "Public transport ridership (Rail passengers only, trips per capita)",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "transport_carbon_emissions",
                "description": "Transport carbon emissions (tons CO2 per capita)",
                "source": "IEA/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
        "effectiveness": [
            {
                "key": "logistics_performance_index",
                "description": "Logistics Performance Index (LPI) score",
                "source": "World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "commute_time",
                "description": "Average commute time (minutes)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },

    "defence": {
        "autonomy": [
            {
                "key": "domestic_defence_production",
                "description": "Domestic defence production (% of procurement)",
                "source": "SIPRI/National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "military_personnel_per_capita",
                "description": "Military personnel per capita",
                "source": "World Bank/SIPRI",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "resilience": [
            {
                "key": "defence_spending_gdp",
                "description": "Defence spending (% of GDP)",
                "source": "SIPRI/World Bank",
                "weight": 0.5,
                "higher_is_better": True,
            },
            {
                "key": "cyber_defence_capability",
                "description": "Cyber defence capability index",
                "source": "National Reports/GCI",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "sustainability": [
            {
                "key": "military_environmental_impact",
                "description": "Military environmental impact (proxy: energy consumption)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": False,
            },
            {
                "key": "veteran_reintegration_programs",
                "description": "Veteran reintegration programs (proxy: spending)",
                "source": "National Reports",
                "weight": 0.5,
                "higher_is_better": True,
            },
        ],
        "effectiveness": [
            {
                "key": "global_peace_index",
                "description": "Global Peace Index score",
                "source": "IEP",
                "weight": 0.5,
                "higher_is_better": True, # Higher score means more peaceful, so better effectiveness
            },
            {
                "key": "conflict_related_deaths",
                "description": "Conflict-related deaths (per 100,000 population)",
                "source": "UCDP/World Bank",
                "weight": 0.5,
                "higher_is_better": False,
            },
        ],
    },
}

# -------------------------------------------------------------------
# API Endpoints / Data Sources
# -------------------------------------------------------------------
DATA_SOURCES = {
    "world_bank": "http://api.worldbank.org/v2",
    "fao": "http://fenixservices.fao.org/faostat/api/v1/en",
    "who": "https://ghoapi.azureedge.net/api",
    "iea": "https://api.iea.org", # Requires API key for most data
    "itu": "https://api.itu.int",
    "imf": "http://dataservices.imf.org/REST/SDMX_JSON.svc",
    "oecd": "https://stats.oecd.org/sdmx-json/data",
    "un_comtrade": "https://comtrade.un.org/api/v1/",
    "un_sdg": "https://unstats.un.org/sdgapi/v1/sdg/",
    "who_unicef_jmp": "https://washdata.org/api", # Placeholder, actual API might differ
    "un_e_waste": "https://ewastemonitor.info/api", # Placeholder, actual API might differ
    "unodc": "https://dataunodc.un.org/api", # Placeholder, actual API might differ
    "sipri": "https://www.sipri.org/databases/milex/api", # Placeholder, actual API might differ
    "iep": "https://www.visionofhumanity.org/api", # Placeholder, actual API might differ
    "ucdp": "https://ucdp.uu.se/api", # Placeholder, actual API might differ
}

# -------------------------------------------------------------------
# Default Weights
# -------------------------------------------------------------------
# Equal weighting unless otherwise defined in INDICATORS
PILLAR_WEIGHTS = {pillar: 0.25 for pillar in PILLARS}
INDUSTRY_WEIGHTS = {industry: 1.0 / len(INDUSTRIES) for industry in INDUSTRIES}
