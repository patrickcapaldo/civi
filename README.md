# Critical Infrastructure Vitals Index (CIVI)

The Critical Infrastructure Vitals Index (CIVI) is a composite index that scores and ranks countries based on the health of their essential infrastructure. It provides a comprehensive snapshot of national capabilities across four critical pillars: Autonomy, Resilience, Sustainability, and Effectiveness.

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

## Methodology

The CIVI score is calculated through a multi-step process:

1.  **Indicator Selection**: A curated set of indicators is chosen for each industry, aligned with the four pillars. Indicators are selected for their relevance, data availability, and global coverage.
2.  **Data Collection**: Data is programmatically fetched from reputable international sources.
3.  **Normalization**: All indicator data is normalized to a common scale (0–100) using a min-max scaling method. This allows for meaningful comparison across different metrics.
4.  **Scoring**: For each country, normalized indicator values are weighted and aggregated to produce a score for each of the four pillars within each industry.
5.  **Aggregation**: Pillar scores are aggregated to create an overall CIVI score for each industry, and industry scores are aggregated to produce a final, country-level CIVI index.

## Data Sources

CIVI is built on public data from trusted global organizations, including:

- World Bank
- Food and Agriculture Organization (FAO)
- International Energy Agency (IEA)
- World Health Organization (WHO)
- International Telecommunication Union (ITU)
- International Monetary Fund (IMF)
- Organisation for Economic Co-operation and Development (OECD)
- United Nations (UN)

## Usage

### 1. Rebuilding the Database

To refresh the CIVI dataset from source, run the master update script. This will fetch the latest data, run all calculations, and regenerate the central JSON database.

```bash
pip install -r requirements.txt
python src/update_data.py
```

This command executes the entire data pipeline and outputs the result to `/data/civi.json`.

### 2. Running Calculations

You can run the data processing steps individually for debugging or partial updates:

- `python src/fetch_data.py`: Downloads raw data.
- `python src/clean_data.py`: Standardizes raw data.
- `python src/process_data.py`: Normalizes and processes data.
- `python src/score_data.py`: Calculates all scores.
- `python src/build_json.py`: Assembles the final `civi.json`.

### 3. Serving the Frontend

The interactive frontend is a React application built for GitHub Pages.

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
