import logging

def get_logger(name):
    """Returns a configured logger."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(name)

def normalize_min_max(data):
    """Scales data to a 0-100 range."""
    if not data: return []
    min_val = min(data)
    max_val = max(data)
    if max_val == min_val:
        return [50 for _ in data] # Or handle as all same
    return [100 * (x - min_val) / (max_val - min_val) for x in data]


COUNTRY_CODES = {
    "USA": "United States",
    "AUS": "Australia",
    # Add all other country mappings
}
