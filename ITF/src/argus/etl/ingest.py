from pathlib import Path
import os
from datetime import datetime, timezone
from uuid import uuid4
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"data"/"generated"
URL = os.getenv("DATABASE_URL","postgresql+psycopg2://argus:argus@localhost:5432/argus")

def main():
    engine=create_engine(URL)
    datasets = {}
    for name in ["students","courses","enrollments","grades","attendance"]:
        path=DATA/f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(path)
        datasets[name]=pd.read_csv(path)

    batch_id = str(uuid4())
    ingested_at = datetime.now(timezone.utc)
    with engine.begin() as c:
        c.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))
        for name, df in datasets.items():
            table=f"raw_{name}"
            c.execute(text(
                f"ALTER TABLE IF EXISTS bronze.{table} "
                "ADD COLUMN IF NOT EXISTS ingestion_batch_id text, "
                "ADD COLUMN IF NOT EXISTS ingested_at timestamptz"
            ))
            df=df.copy()
            df["ingestion_batch_id"] = batch_id
            df["ingested_at"] = ingested_at
            df.to_sql(table,c,schema="bronze",if_exists="append",index=False)
            print(f"bronze.{table}: {len(df):,} rows (batch {batch_id})")

if __name__=="__main__":
    main()
