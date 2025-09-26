
import pandas as pd
from sqlalchemy.orm import Session
from src.core.database import engine
from src.core.models import MetricRaw, MetricCatalog

def create_military_expenditure_per_capita():
    """Calculates military expenditure per capita and saves it as a new raw metric."""
    with Session(engine) as session:
        # Define the new derived metric
        derived_metric_id = "MS.MIL.XPND.PC.CD"
        derived_metric_name = "Military expenditure per capita (current USD)"

        # 1. Add the new metric to the catalog if it doesn't exist
        catalog_entry = session.query(MetricCatalog).filter_by(metric_id=derived_metric_id).first()
        if not catalog_entry:
            new_metric = MetricCatalog(
                metric_id=derived_metric_id,
                name=derived_metric_name,
                industry="Defence",
                pillar="Effectiveness",
                directionality="NEG",  # Assuming higher per capita spending is negative for this index
                units="current USD per capita",
                source="Derived from World Bank",
                description="Military expenditure per capita, derived from MS.MIL.XPND.CD and SP.POP.TOTL."
            )
            session.add(new_metric)
            session.commit()
            print(f"Added derived metric '{derived_metric_name}' to catalog.")

        # 2. Fetch raw data for calculation
        expenditure_data = session.query(MetricRaw).filter_by(metric_id="MS.MIL.XPND.CD").all()
        population_data = session.query(MetricRaw).filter_by(metric_id="SP.POP.TOTL").all()

        if not expenditure_data or not population_data:
            print("Missing raw data for military expenditure or population. Skipping calculation.")
            return

        df_exp = pd.DataFrame([r.__dict__ for r in expenditure_data])
        df_pop = pd.DataFrame([p.__dict__ for p in population_data])

        # 3. Merge dataframes on country and year
        df_merged = pd.merge(df_exp, df_pop, on=["country_code", "year"], suffixes=["_exp", "_pop"])

        # 4. Calculate per capita value
        # Avoid division by zero
        df_merged["metric_value"] = df_merged["metric_value_exp"] / df_merged["metric_value_pop"].replace(0, pd.NA)
        df_merged = df_merged.dropna(subset=["metric_value"])

        # 5. Delete existing derived metric data to avoid duplicates
        session.query(MetricRaw).filter_by(metric_id=derived_metric_id).delete()
        session.commit()

        # 6. Prepare and insert the new derived metric data
        derived_metrics_to_insert = []
        for _, row in df_merged.iterrows():
            derived_metrics_to_insert.append({
                "country_code": row["country_code"],
                "year": int(row["year"]),
                "metric_id": derived_metric_id,
                "metric_value": float(row["metric_value"]),
                "source": "Derived from World Bank"
            })
        
        if derived_metrics_to_insert:
            # Use a bulk merge approach to insert/update
            session.bulk_insert_mappings(MetricRaw, derived_metrics_to_insert)
            session.commit()
            print(f"Successfully inserted/updated {len(derived_metrics_to_insert)} derived military expenditure per capita records.")

def create_all_derived_metrics():
    """Orchestrates the creation of all derived metrics."""
    print("--- Creating derived metrics ---")
    create_military_expenditure_per_capita()
    print("--- Finished creating derived metrics ---")

if __name__ == "__main__":
    create_all_derived_metrics()
