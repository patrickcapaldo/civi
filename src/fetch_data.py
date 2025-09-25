import requests
import pandas as pd
import io
import json
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import MetricCatalog, MetricRaw
from src.config import WORLD_BANK_BASE_URL, WHO_GHO_BASE_URL, ITU_BASE_URL

# FAOSTAT V2 API details
FAOSTAT_API_BASE_URL = "https://fenixservices.fao.org/faostat/api/v2/en/data/"

WHO_GHO_API_URL = "https://ghoapi.azureedge.net/api/{indicator_code}"

def fetch_world_bank_data(session: Session, start_year: int, end_year: int):
    world_bank_metrics = session.query(MetricCatalog).filter_by(source="World Bank").all()
    all_raw_data = []

    for metric in world_bank_metrics:
        print(f"Fetching data for {metric.metric_id} ({metric.name})...")
        url = f"{WORLD_BANK_BASE_URL}/v2/en/indicator/{metric.metric_id}?date={start_year}:{end_year}&format=json&per_page=10000"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and len(data) > 1 and len(data[1]) > 0:
            for entry in data[1]:
                country_code = entry.get('countryiso3code')
                if not country_code and 'country' in entry and 'iso2code' in entry['country']:
                    country_code = entry['country']['iso2code'] # Fallback to ISO2 code
                
                if country_code and entry['value'] is not None:
                    all_raw_data.append({
                        "country_code": country_code,
                        "year": int(entry['date']),
                        "metric_id": metric.metric_id,
                        "metric_value": float(entry['value']),
                        "units": metric.units,
                        "source": metric.source,
                    })