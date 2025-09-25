from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint, CHAR
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class MetricCatalog(Base):
    __tablename__ = 'metrics_catalog'
    metric_id = Column(String(100), primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    industry = Column(String(50), nullable=False)
    pillar = Column(String(50), nullable=False)
    units = Column(String(50))
    directionality = Column(CHAR(3), comment="POS = higher is better, NEG = lower is better")
    source = Column(String)
    source_url = Column(String)
    coverage_notes = Column(String)

class MetricRaw(Base):
    __tablename__ = 'metrics_raw'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False)
    year = Column(Integer, nullable=False)
    metric_id = Column(String(100), ForeignKey('metrics_catalog.metric_id'), nullable=False)
    metric_value = Column(Float)
    units = Column(String(50))
    source = Column(String)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint('country_code', 'year', 'metric_id', name='_country_year_metric_uc'),)

class MetricNormalized(Base):
    __tablename__ = 'metrics_normalized'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False)
    year = Column(Integer, nullable=False)
    metric_id = Column(String(100), ForeignKey('metrics_catalog.metric_id'), nullable=False)
    normalized_value = Column(Float)
    normalization_method = Column(String(50))
    normalization_window = Column(String(50))
    __table_args__ = (UniqueConstraint('country_code', 'year', 'metric_id', name='_norm_country_year_metric_uc'),)

class PillarScore(Base):
    __tablename__ = 'pillar_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False)
    year = Column(Integer, nullable=False)
    industry = Column(String(50), nullable=False)
    pillar = Column(String(50), nullable=False)
    pillar_score = Column(Float)
    __table_args__ = (UniqueConstraint('country_code', 'year', 'industry', 'pillar', name='_pillar_country_year_industry_pillar_uc'),)

class IndustryScore(Base):
    __tablename__ = 'industry_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False)
    year = Column(Integer, nullable=False)
    industry = Column(String(50), nullable=False)
    industry_score = Column(Float)
    __table_args__ = (UniqueConstraint('country_code', 'year', 'industry', name='_industry_country_year_industry_uc'),)

class CountryScore(Base):
    __tablename__ = 'country_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_code = Column(String(3), nullable=False)
    year = Column(Integer, nullable=False)
    country_score = Column(Float)
    __table_args__ = (UniqueConstraint('country_code', 'year', name='_country_year_uc'),)

class NormalizationLog(Base):
    __tablename__ = 'normalization_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(String(100), ForeignKey('metrics_catalog.metric_id'), nullable=False)
    run_id = Column(String(100))
    normalization_method = Column(String(50))
    window_start_year = Column(Integer)
    window_end_year = Column(Integer)
    min_value = Column(Float)
    max_value = Column(Float)
    log_timestamp = Column(DateTime(timezone=True), server_default=func.now())

class EtlRun(Base):
    __tablename__ = 'etl_runs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(100))
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(20))
    records_processed = Column(Integer)
    notes = Column(String)
