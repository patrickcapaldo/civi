import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api import app
from src.database import get_db
from src.models import Base, MetricCatalog, MetricRaw, MetricNormalized, PillarScore, IndustryScore, CountryScore
from src.populate_catalog import populate_metrics_catalog, METRICS
from src.fetch_data import fetch_world_bank_data
from src.process_data import normalize_data
from src.score_data import aggregate_scores
import os

# Use a test database URL (e.g., an in-memory SQLite for unit tests, or a dedicated PostgreSQL test DB)
# For simplicity, we'll use the main DATABASE_URL for now, assuming it's a test instance or can be reset.
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://patrick:password@localhost/civi")

@pytest.fixture(scope="module")
def test_db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    # Drop and recreate tables for a clean test environment
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="module")
def test_db_session(test_db_engine):
    connection = test_db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="module")
def setup_data(test_db_session):
    # Populate and process data for API tests
    populate_metrics_catalog()
    fetch_world_bank_data(start_year=2000, end_year=2023) # Use a wider range for testing
    normalize_data()
    aggregate_scores()
    test_db_session.commit() # Commit changes to make them visible to the API

@pytest.fixture(scope="module")
def client(setup_data, test_db_session):
    # Override the get_db dependency to use our test session
    def override_get_db():
        yield test_db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_read_countries(client):
    response = client.get("/countries")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "country_code" in response.json()[0]

def test_read_country_profile(client, test_db_session):
    # Find a country and year that has data
    sample_score = test_db_session.query(CountryScore).first()
    if not sample_score:
        pytest.skip("No country scores found in the database for testing.")
    
    country_code = sample_score.country_code
    year = sample_score.year

    response = client.get(f"/countries/{country_code}?year={year}")
    assert response.status_code == 200
    data = response.json()
    assert data["country_code"] == country_code
    assert len(data["country_scores"]) > 0
    assert len(data["industry_scores"]) > 0
    assert len(data["pillar_scores"]) > 0
    assert len(data["metrics"]) > 0

def test_read_country_profile_not_found(client):
    response = client.get("/countries/XYZ")
    assert response.status_code == 404

def test_read_industry_comparison(client, test_db_session):
    # Find an industry and year that has data
    sample_score = test_db_session.query(IndustryScore).first()
    if not sample_score:
        pytest.skip("No industry scores found in the database for testing.")
    
    industry_name = sample_score.industry
    year = sample_score.year

    response = client.get(f"/industries/{industry_name}?year={year}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "industry" in response.json()[0]

def test_read_pillar_comparison(client, test_db_session):
    # Find a pillar and year that has data
    sample_score = test_db_session.query(PillarScore).first()
    if not sample_score:
        pytest.skip("No pillar scores found in the database for testing.")
    
    pillar_name = sample_score.pillar
    year = sample_score.year

    response = client.get(f"/pillars/{pillar_name}?year={year}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "pillar" in response.json()[0]

def test_read_timeseries_country(client, test_db_session):
    sample_score = test_db_session.query(CountryScore).first()
    if not sample_score:
        pytest.skip("No country scores found in the database for testing.")
    
    country_code = sample_score.country_code

    response = client.get(f"/scores/timeseries?country={country_code}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "year" in response.json()[0]
    assert "score" in response.json()[0]

def test_read_timeseries_country_industry(client, test_db_session):
    sample_score = test_db_session.query(IndustryScore).first()
    if not sample_score:
        pytest.skip("No industry scores found in the database for testing.")
    
    country_code = sample_score.country_code
    industry_name = sample_score.industry

    response = client.get(f"/scores/timeseries?country={country_code}&industry={industry_name}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "year" in response.json()[0]
    assert "score" in response.json()[0]

def test_read_timeseries_country_industry_pillar(client, test_db_session):
    sample_score = test_db_session.query(PillarScore).first()
    if not sample_score:
        pytest.skip("No pillar scores found in the database for testing.")
    
    country_code = sample_score.country_code
    industry_name = sample_score.industry
    pillar_name = sample_score.pillar

    response = client.get(f"/scores/timeseries?country={country_code}&industry={industry_name}&pillar={pillar_name}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "year" in response.json()[0]
    assert "score" in response.json()[0]

def test_read_timeseries_invalid_query(client):
    response = client.get("/scores/timeseries") # No country provided
    assert response.status_code == 422
