![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-Dual_License-blue)

# Critical Infrastructure Vitals Index (CIVI)

<p align="center">
  <img src="assets/img/civi_explore_03.png" width="600" />
</p>

## Why CIVI Matters

In an interconnected world, the strength of a nation's critical infrastructure is a primary determinant of its economic stability, national security, and quality of life. CIVI provides a standardized framework for policymakers, researchers, and investors to:
- Benchmark national infrastructure performance.
- Identify strategic vulnerabilities and strengths.
- Guide policy and investment decisions.
- Promote global standards for infrastructure development.

## The Four Pillars

CIVI evaluates infrastructure across four distinct dimensions:

1.  **Autonomy**: A nation's ability to operate its critical systems without dependence on foreign entities. This includes control over resources, technology, and supply chains.
2.  **Resilience**: The capacity of infrastructure to withstand, adapt to, and recover from disruptions, whether natural disasters, cyber-attacks, or economic shocks.
3.  **Sustainability**: The environmental, social, and economic viability of infrastructure. This pillar measures the long-term impact and efficiency of resource use.
4.  **Effectiveness**: The quality, accessibility, and performance of infrastructure services delivered to citizens and businesses.

## Industries Covered

CIVI spans the following 11 critical industries:

- Communications
- Defence
- Energy
- Finance
- Food & Agriculture
- Healthcare
- Transport
- Water
- Waste Management
- Emergency Services
- Information Technology

## Key Features

### Explore Page

The Explore page serves as the primary entry point for visualizing the CIVI data. It features an interactive world map where users can:

- **Visualize Country Scores:** Hover over any country to see its overall CIVI score and a breakdown across the four pillars (Autonomy, Resilience, Sustainability, Effectiveness).
- **Filter by Industry and Pillar:** Use dropdown menus to filter the map display, showing how countries perform in specific industries (e.g., Energy, Healthcare) or within particular pillars.
- **Dynamic Data Display:** The map dynamically updates to reflect the selected filters, providing a quick and intuitive way to understand global critical infrastructure landscapes.

<p align="center">
  <img src="assets/img/civi_explore_02.png" width="600" />
</p>

### Analyse Page

The Analyse page offers a deeper dive into historical trends and comparative analysis. On this page, users can:

- **Historical Data & Comparison:** Select multiple countries, industries, and pillars to compare their historical CIVI scores over time.
- **Customizable Line Colors:** For each selected data series, users can choose a custom line color using an integrated color picker, both before adding to the comparison and after. This allows for personalized and clear visualization of comparative data.
- **Dynamic Charting:** The page features a dynamic line chart that visualizes the selected historical data, making it easy to identify trends and compare performance across different selections.
- **Flexible Timeframe:** Adjust the start and end years to focus on specific periods of interest for historical analysis.

<p align="center">
  <img src="assets/img/civi_analyse_02.png" width="600" />
</p>
<p align="center">
  <img src="assets/img/civi_analyse_01.png" width="600" />
</p>

## Methodology

The CIVI score is calculated through a multi-step process:

1.  **Indicator Selection**: A curated set of indicators is chosen for each industry, aligned with the four pillars. Indicators are selected for their relevance, data availability, and global coverage.
2.  **Data Collection**: Data is programmatically fetched from reputable international sources and stored in a PostgreSQL database.
3.  **Normalization**: All indicator data is normalized to a common scale (0–100) using a min-max scaling method. This allows for meaningful comparison across different metrics.
4.  **Scoring**: For each country, normalized indicator values are weighted and aggregated to produce a score for each of the four pillars within each industry.
5.  **Aggregation**: Pillar scores are aggregated to create an overall CIVI score for each industry, and industry scores are aggregated to produce a final, country-level CIVI index.

## Data Sources

CIVI is built on public data from trusted global organizations, including:

- World Bank
- Food and Agriculture Organization (FAO) (SDMX API - partially implemented)
- International Energy Agency (IEA)
- World Health Organization (WHO)
- International Telecommunication Union (ITU)
- International Monetary Fund (IMF)
- Organisation for Economic Co-operation and Development (OECD)
- United Nations (UN)

## Tech Stack

The CIVI project is built using the following technologies:

-   **Database**: PostgreSQL
-   **Backend**: Python, FastAPI
-   **Frontend**: React (JavaScript)
-   **Data Visualization**: Chart.js, D3.js

## Quick Start

The fastest way to get the CIVI application up and running is by using Docker Compose.

1.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This command will:
    -   Build the Docker images for the backend (FastAPI) and frontend (React).
    -   Start the PostgreSQL database, backend API, and frontend application.
    -   The frontend will be accessible at `http://localhost:3000`.
    -   The backend API will be accessible at `http://localhost:8000`.

2.  **Manual Quick Start (without Docker Compose):**

    If you prefer to run components manually:

    **Backend (API):**
    ```bash
    # From the project root
    uvicorn src.api.main:app --reload
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

    **Frontend:**
    ```bash
    # From the project root
    cd frontend
    npm install
    npm start
    ```
    The frontend will be accessible at `http://localhost:3000`.

## Detailed Usage

Before running the following commands, ensure your Python virtual environment is activated:

```bash
source .venv/bin/activate
```

This project utilizes a PostgreSQL database for data storage, a Python-based ETL pipeline for data ingestion and processing, and a FastAPI application to expose the data.

### 1. Database Setup

Ensure you have a PostgreSQL server running and accessible. You will need to create a database and a user with appropriate permissions.

1.  **Create Database and User:**
    ```bash
    sudo -i -u postgres
    psql
    # Inside psql:
    CREATE USER patrick WITH PASSWORD 'password'; # Replace 'patrick' and 'password' with your desired credentials
    CREATE DATABASE civi OWNER patrick;
    GRANT ALL PRIVILEGES ON DATABASE civi TO patrick;
    GRANT CREATE ON SCHEMA public TO patrick;
    \q
    exit
    ```
2.  **Configure Database Connection:**
    Create a `.env` file in the project root with your database connection string:
    ```
    DATABASE_URL=postgresql://patrick:password@localhost/civi
    ```
    (Replace `patrick` and `password` with your credentials, and `localhost/civi` with your database host/name if different).
3.  **Apply Database Schema:**
    ```bash
    psql -h localhost -U patrick -d civi -f civi_schema.sql
    ```
    (Enter your password when prompted).

### 2. ETL Pipeline (Data Ingestion and Processing)

This pipeline fetches raw data, normalizes it, and aggregates scores into the PostgreSQL database.

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Populate Metric Catalog:**
    This script initializes the `metrics_catalog` table with definitions of the metrics to be fetched.
    ```bash
    python -m src.populate_catalog
    ```
3.  **Fetch Raw Data:**
    This fetches data from configured external APIs (e.g., World Bank, FAOSTAT) and stores it in `metrics_raw`.
    ```bash
    python -m src.fetch_data
    ```
4.  **Normalize Data:**
    Normalizes raw data to a 0-100 scale and stores it in `metrics_normalized`.
    ```bash
    python -m src.process_data
    ```
5.  **Aggregate Scores:**
    Aggregates normalized data into pillar, industry, and country scores.
    ```bash
    python -m src.score_data
    ```

### 3. API Server

The FastAPI application exposes the processed CIVI data via REST endpoints.

1.  **Start the API Server:**
    ```bash
    uvicorn src.api.main:app --reload
    ```
    The API will be accessible at `http://127.0.0.1:8000`.
2.  **Explore API Documentation:**
    Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### 4. Running Tests

To ensure the correctness of the ETL pipeline and API endpoints:

1.  **Run ETL Tests:**
    ```bash
    pytest tests/test_etl.py
    ```
    > ⚠️ **Warning**: These tests will drop and recreate all tables in your configured database, deleting all existing data.
2.  **Run API Tests:**
    ```bash
    pytest tests/test_api.py
    ```
    > ⚠️ **Warning**: These tests will also drop and recreate all tables and run the entire ETL pipeline to populate data before testing the API.

### 5. Serving the Frontend

The interactive frontend is a React application.

To run locally:

```bash
cd frontend
npm install
npm start
```

To build for deployment:

```bash
cd frontend
npm run build
```

### 7. Updating Data and Static JSONs

To ensure data consistency and prevent visualization issues on the frontend, a dedicated script is provided to fetch new data, process it, update the PostgreSQL database, and then generate/update the static JSON files used by the frontend. This process includes validation steps to ensure data integrity.

1.  **Run the Update Script:**
    ```bash
    ./update_data.sh
    ```
    This script will perform the following actions:
    *   **ETL Pipeline:** Fetches raw data, populates the catalog, processes data, and aggregates scores into the PostgreSQL database.
    *   **Database Tests:** Runs `pytest tests/test_etl.py` to validate the data in PostgreSQL. If these tests fail, the process will stop.
    *   **Generate Static JSONs:** Creates or updates the static JSON files in `frontend/public/civi_modular/` from the processed data in PostgreSQL.
    *   **Frontend Data Validation:** Performs basic checks (e.g., verifies the existence of key JSON files) to ensure the generated static files are present. (Note: More comprehensive frontend data validation tests can be added to `frontend/package.json` and executed here if needed).

    **Important:** This script ensures that only valid and correctly formatted data is propagated to the static JSON files, preventing potential visualization issues on the frontend.

## Contributing

We welcome contributions to the CIVI project! To contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes, adhering to the existing code style and conventions.
4.  Write and run tests to ensure your changes work as expected.
5.  Submit a pull request with a clear description of your changes.

## License

This project is dual-licensed:

-   **Software (codebase)**: Licensed under the [Polyform Noncommercial License 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/).
-   **Data, documentation, and other non-code content**: Licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

Please see the [LICENSE](LICENSE) file for full details on both licenses.