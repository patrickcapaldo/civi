import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

WORLD_BANK_BASE_URL = os.getenv("WORLD_BANK_BASE_URL", "http://api.worldbank.org")
WHO_GHO_BASE_URL = os.getenv("WHO_GHO_BASE_URL", "https://ghoapi.azureedge.net/who")
ITU_BASE_URL = os.getenv("ITU_BASE_URL", "https://api.datahub.itu.int/v2")

# --- Added variables ---
LAST_UPDATED = datetime.now().strftime("%Y-%m-%d")
VERSION = "1.0.0"

DATA_SOURCES = {
    "World Bank": "https://data.worldbank.org/",
    "ITU": "https://datahub.itu.int/",
    "FAOSTAT": "http://www.fao.org/faostat/en/#data",
}

INDUSTRIES = [
    "Communications",
    "Defence",
    "Energy",
    "Finance",
    "Food & Agriculture",
    "Healthcare",
    "Transport",
    "Water",
    "Waste Management",
    "Emergency Services",
    "Information Technology",
]
