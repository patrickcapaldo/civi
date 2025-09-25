import uuid
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import engine
from src.core.models import MetricCatalog, MetricRaw, MetricNormalized, NormalizationLog

def process_all():
    """Normalizes raw metric data and stores it in the metrics_normalized table."""
    with Session(engine) as session:
        # Fetch all raw data
        raw_metrics = session.query(MetricRaw).all()
        if not raw_metrics:
            print("No raw metrics to normalize.")
            return

        df_raw = pd.DataFrame([r.__dict__ for r in raw_metrics])
        # Drop SQLAlchemy internal state if present
        df_raw = df_raw.drop(columns=['_sa_instance_state'], errors='ignore')

        # Fetch metric catalog for directionality
        metric_catalog = session.query(MetricCatalog).all()
        df_catalog = pd.DataFrame([m.__dict__ for m in metric_catalog])
        df_catalog = df_catalog.drop(columns=['_sa_instance_state'], errors='ignore')
        df_catalog = df_catalog[['metric_id', 'directionality']]

        df_merged = pd.merge(df_raw, df_catalog, on='metric_id', how='left')

        normalized_data = []
        normalization_logs = []

        # Process each metric_id for normalization
        for metric_id in df_merged['metric_id'].unique():
            metric_df = df_merged[df_merged['metric_id'] == metric_id].copy()
            directionality = metric_df['directionality'].iloc[0]

            min_val = metric_df['metric_value'].min()
            max_val = metric_df['metric_value'].max()

            if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
                print(f"Skipping normalization for {metric_id}: insufficient data or min/max are equal.")
                continue

            # Min-Max Scaling to 0-100
            metric_df['normalized_value'] = (
                (metric_df['metric_value'] - min_val) / (max_val - min_val)
            ) * 100

            # Handle directionality
            if directionality == 'NEG':
                metric_df['normalized_value'] = 100 - metric_df['normalized_value']
            
            # Prepare data for insertion
            for _, row in metric_df.iterrows():
                normalized_data.append({
                    'country_code': row['country_code'],
                    'year': row['year'],
                    'metric_id': row['metric_id'],
                    'normalized_value': row['normalized_value'],
                    'normalization_method': 'min-max',
                    'normalization_window': f'{df_raw['year'].min()}-{df_raw['year'].max()}' # Global window for now
                })
            
            # Log normalization parameters
            normalization_logs.append({
                'metric_id': metric_id,
                'normalization_method': 'min-max',
                'window_start_year': df_raw['year'].min(),
                'window_end_year': df_raw['year'].max(),
                'min_value': min_val,
                'max_value': max_val,
                'run_id': str(uuid.uuid4()) # Use Python's UUID for portability
            })
        
        if normalized_data:
            # Clear existing normalized data to avoid duplicates on re-run
            session.query(MetricNormalized).delete()
            session.bulk_insert_mappings(MetricNormalized, normalized_data)
            print(f"Successfully inserted {len(normalized_data)} normalized data points into metrics_normalized.")
        else:
            print("No normalized data to insert.")

            # Convert numpy types to native Python types for psycopg2 compatibility
            for log in normalization_logs:
                log['window_start_year'] = int(log['window_start_year'])
                log['window_end_year'] = int(log['window_end_year'])
                log['min_value'] = float(log['min_value'])
                log['max_value'] = float(log['max_value'])
            # Clear existing normalization logs for these metrics
            # This is a simplified approach; a more robust system would track run_ids
            for log in normalization_logs:
                session.query(NormalizationLog).filter(NormalizationLog.metric_id == log['metric_id']).delete()
            session.bulk_insert_mappings(NormalizationLog, normalization_logs)
            print(f"Successfully inserted {len(normalization_logs)} normalization logs.")
        
        session.commit()

if __name__ == "__main__":
    process_all()