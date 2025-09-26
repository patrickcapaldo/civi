import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, MetricCatalog, MetricRaw, MetricNormalized, PillarScore, IndustryScore, CountryScore, NormalizationLog
from src.populate_catalog import populate_metrics_catalog, METRICS
from src.fetch_data import fetch_world_bank_data
from src.process_data import normalize_data
from src.score_data import aggregate_scores
import os

# Use a test database URL (e.g., an in-memory SQLite for unit tests, or a dedicated PostgreSQL test DB)
# For simplicity, we'll use the main DATABASE_URL for now, assuming it's a test instance or can be reset.
# In a real-world scenario, you'd use a separate test database.
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://<user>:<password>@localhost/civi")

@pytest.fixture(scope="module")
def test_db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    # Drop and recreate tables for a clean test environment
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
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

def test_populate_catalog(test_db_session):
    populate_metrics_catalog()
    metrics = test_db_session.query(MetricCatalog).all()
    assert len(metrics) == len(METRICS)
    assert test_db_session.query(MetricCatalog).filter_by(metric_id='IT.NET.USER.ZS').first() is not None

# This test will actually hit the World Bank API, so it's more of an integration test.
# In a true unit test, you would mock the requests.get call.
def test_fetch_world_bank_data(test_db_session):
    # Ensure catalog is populated first
    populate_metrics_catalog()
    fetch_world_bank_data(start_year=2020, end_year=2020) # Fetch a small range for testing
    raw_data = test_db_session.query(MetricRaw).all()
    assert len(raw_data) > 0 # Expect some data to be fetched
    assert test_db_session.query(MetricRaw).filter_by(metric_id='IT.NET.USER.ZS', year=2020).first() is not None

def test_normalize_data(test_db_session):
    # Ensure raw data is present
    populate_metrics_catalog()
    fetch_world_bank_data(start_year=2020, end_year=2020)
    normalize_data()
    normalized_data = test_db_session.query(MetricNormalized).all()
    assert len(normalized_data) > 0
    assert all(0 <= d.normalized_value <= 100 for d in normalized_data)
    assert test_db_session.query(NormalizationLog).count() > 0

def test_aggregate_scores(test_db_session):
    # Ensure normalized data is present
    populate_metrics_catalog()
    fetch_world_bank_data(start_year=2020, end_year=2020)
    normalize_data()
    aggregate_scores()

    assert test_db_session.query(PillarScore).count() > 0
    assert test_db_session.query(IndustryScore).count() > 0
    assert test_db_session.query(CountryScore).count() > 0

    # Check a sample country score
    sample_country_score = test_db_session.query(CountryScore).filter(CountryScore.country_code == 'USA', CountryScore.year == 2020).first()
    if sample_country_score:
        assert 0 <= sample_country_score.country_score <= 100
