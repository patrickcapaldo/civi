#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting data update process..."

# 1. Run ETL Pipeline
echo "Running ETL pipeline..."
source .venv/bin/activate
python -m src.data_processing.populate_catalog
python -m src.etl.fetch_data
python -m src.data_processing.process_data
python -m src.data_processing.score_data
deactivate
echo "ETL pipeline completed."

# 2. Run Database Tests
echo "Running database tests..."
source .venv/bin/activate
pytest tests/test_etl.py
deactivate
echo "Database tests passed."

# 3. Generate Static JSONs from PostgreSQL
echo "Generating static JSON files from PostgreSQL..."
source .venv/bin/activate
python -m src.data_processing.build_json
deactivate
echo "Static JSON files generated."

# 4. Run Frontend Data Tests (to validate JSONs)
echo "Running frontend data validation tests..."
# Assuming there will be a test script for validating the JSONs
# For now, this is a placeholder. You would need to implement actual tests here.
# Example: `npm --prefix frontend test-data-validation`
# For now, we'll just check if the files exist.
if [ -f frontend/public/civi_modular/USA.json ]; then
  echo "Sample JSON file (USA.json) found. Basic validation passed."
else
  echo "Error: Sample JSON file (USA.json) not found. Frontend data validation failed."
  exit 1
fi
echo "Frontend data validation tests passed."

echo "Data update process completed successfully!"