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
# -------------------------------------------------------------------
INDICATORS = {
    "energy": {
        "autonomy": [
            {
                "key": "energy_import_dependency",
                "description": "Share of energy supply that is imported (%)",
                "source": "IEA/World Bank",
                "weight": 0.6,
            },
            {
                "key": "energy_source_diversity",
                "description": "Diversity index (HHI) of domestic energy sources",
                "source": "IEA",
                "weight": 0.4,
            },
        ],
        "resilience": [
            {
                "key": "electricity_outage_duration",
                "description": "Average annual outage duration (SAIDI)",
                "source": "World Bank",
                "weight": 0.5,
            },
            {
                "key": "strategic_reserves_days",
                "description": "Days of strategic fuel reserves available",
                "source": "IEA",
                "weight": 0.5,
            },
        ],
        "sustainability": [
            {
                "key": "renewables_share_percent",
                "description": "Share of renewables in total energy (%)",
                "source": "IEA",
                "weight": 0.5,
            },
            {
                "key": "carbon_intensity",
                "description": "CO₂ emissions per kWh electricity (gCO2/kWh)",
                "source": "IEA",
                "weight": 0.5,
            },
        ],
        "effectiveness": [
            {
                "key": "electricity_access_percent",
                "description": "Population with access to electricity (%)",
                "source": "World Bank",
                "weight": 0.5,
            },
            {
                "key": "electricity_cost_share_income",
                "description": "Household electricity cost as % of income",
                "source": "OECD/World Bank",
                "weight": 0.5,
            },
        ],
    },

    "food_agriculture": {
        "autonomy": [
            {
                "key": "food_import_dependency",
                "description": "Food import dependency ratio (%)",
                "source": "FAO",
                "weight": 0.7,
            },
            {
                "key": "agricultural_land_per_capita",
                "description": "Hectares of agricultural land per capita",
                "source": "FAO/World Bank",
                "weight": 0.3,
            },
        ],
        "resilience": [
            {
                "key": "cereal_stock_to_use",
                "description": "Cereal stock-to-use ratio (%)",
                "source": "FAO",
                "weight": 0.6,
            },
            {
                "key": "ag_insurance_coverage",
                "description": "Agricultural insurance coverage (proxy index)",
                "source": "World Bank",
                "weight": 0.4,
            },
        ],
        "sustainability": [
            {
                "key": "water_use_per_ag_gdp",
                "description": "Cubic meters of water per unit of agricultural GDP",
                "source": "FAO AQUASTAT",
                "weight": 0.5,
            },
            {
                "key": "fertilizer_use_intensity",
                "description": "Fertilizer use (kg/ha)",
                "source": "FAO",
                "weight": 0.5,
            },
        ],
        "effectiveness": [
            {
                "key": "undernourishment_prevalence",
                "description": "Share of population undernourished (%)",
                "source": "FAO",
                "weight": 0.5,
            },
            {
                "key": "food_price_index",
                "description": "National food price index (normalized)",
                "source": "FAO",
                "weight": 0.5,
            },
        ],
    },

    # ... Repeat pattern for communications, defence, healthcare, etc.
}

# -------------------------------------------------------------------
# API Endpoints / Data Sources
# -------------------------------------------------------------------
DATA_SOURCES = {
    "world_bank": "http://api.worldbank.org/v2",
    "fao": "http://fenixservices.fao.org/faostat/api/v1/en",
    "who": "https://ghoapi.azureedge.net/api",
    "iea": "https://api.iea.org",
    "itu": "https://api.itu.int",
    "imf": "https://dataservices.imf.org",
    "oecd": "https://stats.oecd.org/sdmx-json/data",
}

# -------------------------------------------------------------------
# Default Weights
# -------------------------------------------------------------------
# Equal weighting unless otherwise defined in INDICATORS
PILLAR_WEIGHTS = {pillar: 0.25 for pillar in PILLARS}
INDUSTRY_WEIGHTS = {industry: 1.0 / len(INDUSTRIES) for industry in INDUSTRIES}
