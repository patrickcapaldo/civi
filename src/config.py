import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

WORLD_BANK_BASE_URL = os.getenv("WORLD_BANK_BASE_URL", "http://api.worldbank.org")
WHO_GHO_BASE_URL = os.getenv("WHO_GHO_BASE_URL", "https://ghoapi.azureedge.net/who")
ITU_BASE_URL = os.getenv("ITU_BASE_URL", "https://api.datahub.itu.int/v2")