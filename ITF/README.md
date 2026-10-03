# ARGUS — Academic Risk & Guidance Analytics System

ARGUS is a data-engineering-first academic decision-support platform that ingests student academic records, validates them, transforms them through a Bronze/Silver/Gold architecture, calculates explainable academic-risk indicators, and presents results through a Streamlit dashboard.

> ARGUS supports academic monitoring. It does not diagnose students, make disciplinary decisions, or replace qualified counselors/advisors.

## Architecture
```text
Source CSV / Synthetic Data
          ↓
     Python Ingestion
          ↓
  Bronze PostgreSQL
          ↓
  Data Quality Checks
          ↓
        dbt ELT
          ↓
  Silver PostgreSQL
          ↓
   Risk Analytics/ML
          ↓
   Gold PostgreSQL
          ↓
    Streamlit Dashboard
```
Airflow orchestrates the workflow.

## Repository
`src/` ETL, validation and analytics · `dbt/` warehouse transformations · `airflow/` orchestration · `dashboard/` UI · `tests/` automated tests · `docs/` engineering standards.

## Quick Start
Requirements: Docker Desktop and Git.

The project core is designed to run reliably without Airflow; Airflow is an optional profile for orchestration and should be started explicitly when needed.

```bash
docker compose up --build -d postgres dashboard

docker compose run --rm dashboard python scripts/generate_data.py
docker compose run --rm dashboard python -m argus.etl.ingest
docker compose run --rm dashboard python -m argus.quality.validate
docker compose run --rm dashboard dbt build --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
docker compose run --rm dashboard python -m argus.analytics.risk_engine
```

Dashboard: http://localhost:8501

## Database Layers
- `bronze`: `raw_students`, `raw_courses`, `raw_enrollments`, `raw_grades`, and `raw_attendance` retain append-only ingestion batches. Silver staging models select the latest batch.
- `silver`: cleaned staging views and `student_academic_performance`, one row per student and semester for risk modeling.
- `gold`: `dim_students`, `dim_courses`, `dim_semester`, `fact_enrollments`, `fact_grades`, `fact_attendance`, plus risk scores and model metrics.

The generated data has semester numbers but no calendar dates, so the warehouse uses `dim_semester`; a true `dim_date` requires dated source records.

Optional Airflow stack:

```bash
docker compose --profile airflow up -d airflow-init airflow-webserver airflow-scheduler
```

Airflow: http://localhost:8080  
The optional Compose setup does not create an Airflow login user. Create/configure an account before using or exposing the webserver.

## Tests
```bash
docker compose run --rm dashboard pytest -q
```

## Documentation
- `docs/TECHNICAL_DOCUMENTATION.md` — architecture and engineering specification
- `docs/PROJECT_DEFENSE.md` — project rationale, demo outline, results, and defense questions
- `docs/PROJECT_DOCUMENTATION.md` — requirements and project specification
- `docs/DATA_DICTIONARY.md` — data contract/reference
- `docs/MODEL_CARD.md` — model governance
- `docs/SECURITY_AND_PRIVACY.md` — security and responsible-use controls
- `docs/PROJECT_TIMELINE.md` — 12-week delivery plan
