# ARGUS Technical Guide

ARGUS (Academic Risk & Guidance Analytics System) is a local academic-data pipeline and dashboard. This guide explains how to run it, where the code lives, how records move through PostgreSQL, what key code does, and what the model can and cannot tell you.

ARGUS is a prototype for academic monitoring. It is not a diagnosis, a disciplinary decision, or a substitute for qualified human review. The included data is synthetic.

## 1. At A Glance

```text
generate_data.py
	-> five CSV files
	-> etl.ingest appends one tagged batch to PostgreSQL bronze.raw_*
	-> quality.validate checks raw data
	-> dbt builds Silver views/tables and Gold dimensions/facts
	-> analytics.risk_engine trains a baseline model and writes risk outputs
	-> Streamlit reads the risk outputs and shows the dashboard
```

Docker Compose starts PostgreSQL and the dashboard. Airflow is an optional profile; it is not needed for the recommended manual pipeline.

## 2. Requirements And Services

- Docker with Docker Compose v2.
- Ports `5432` (PostgreSQL), `8501` (dashboard), and optionally `8080` (Airflow) available.
- Git is required for the CI workflow and is checked by `dbt debug`; the core dbt build does not fetch Git dependencies.

| Service | Image/runtime | Port | Role |
|---|---|---:|---|
| `postgres` | PostgreSQL 16 | 5432 | Persistent database and warehouse |
| `dashboard` | Project Dockerfile, Python 3.11 | 8501 | Pipeline command environment and Streamlit UI |
| `airflow-init` | Airflow 2.10.3 | none | Optional Airflow metadata migration |
| `airflow-webserver` | Airflow 2.10.3 | 8080 | Optional workflow UI |
| `airflow-scheduler` | Airflow 2.10.3 | none | Optional DAG scheduler |

The development database defaults are database/user/password `argus` and port `5432`. These values are public demo credentials, not production secrets. `docker-compose.yml` maps `host.docker.internal` to Docker's host gateway; this is used because some nested Docker environments cannot route directly between sibling containers. `DBT_HOST` can override that address if needed.

## 3. Start And Run

Run these commands from the project directory (`ITF/`). The first command builds the app image so the pinned dbt Core and Postgres adapter versions are installed.

```bash
docker compose up --build -d postgres dashboard
docker compose ps

docker compose run --rm dashboard python scripts/generate_data.py
docker compose run --rm dashboard python -m argus.etl.ingest
docker compose run --rm dashboard python -m argus.quality.validate
docker compose run --rm dashboard dbt build --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
docker compose run --rm dashboard python -m argus.analytics.risk_engine
```

`docker compose run --rm dashboard ...` starts a temporary container with the same image, environment, mounted workspace, and database route as the dashboard service. The steps are sequential: do not run dbt before ingestion and validation, or the risk engine before dbt has created `silver.student_academic_performance`.

Open the dashboard at <http://localhost:8501>. It shows a data-not-available message until the risk engine has populated Gold outputs. Streamlit caches dashboard data for up to 60 seconds.

Run automated tests with:

```bash
docker compose run --rm dashboard pytest -q
```

To check the database and dbt connection:

```bash
docker compose exec -T postgres pg_isready -U argus -d argus
docker compose run --rm dashboard dbt debug --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
```

`dbt debug` can report that Git is missing from the slim app image even when its Postgres connection check succeeds. This repository has no Git-sourced dbt dependencies; confirm the `Connection test` result separately.

## 4. Reset Data Safely

Ingestion is append-only. A normal repeat run creates another Bronze batch, and Silver uses only the newest batch. To start with empty raw tables while keeping the Docker volume, generated files, and schemas, run:

```bash
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U argus -d argus -c 'TRUNCATE TABLE bronze.raw_students, bronze.raw_courses, bronze.raw_enrollments, bronze.raw_grades, bronze.raw_attendance;'
```

Then run the pipeline commands from section 3. dbt rebuilds its tables/views and the risk engine replaces its two output tables. The `pgdata` named volume persists across container restarts.

To remove the whole local database volume, including all PostgreSQL data, use `docker compose down -v`. This is destructive: the next start creates a new database. `sql/init.sql` runs only when PostgreSQL initializes an empty data directory; editing that file does not rerun it against an existing volume.

## 5. Database And Data Lineage

`sql/init.sql` creates only the `bronze`, `silver`, and `gold` schemas. Python ingestion creates the Bronze tables. dbt creates the Silver and Gold relations. For the default 1,000-student/four-semester dataset, a successful run produces the approximate counts below.

| Layer | Relation | Materialization and grain | Typical rows |
|---|---|---|---:|
| Bronze | `bronze.raw_students` | Table; student per ingestion batch | 1,000 per batch |
| Bronze | `bronze.raw_courses` | Table; course per batch | 10 per batch |
| Bronze | `bronze.raw_enrollments` | Table; enrollment per batch | 34,996 per batch |
| Bronze | `bronze.raw_grades` | Table; graded enrollment per batch | 34,996 per batch |
| Bronze | `bronze.raw_attendance` | Table; student-course-semester per batch | 34,996 per batch |
| Silver | `silver.stg_students` | View; student, latest batch only | 1,000 |
| Silver | `silver.stg_courses` | View; course, latest batch only | 10 |
| Silver | `silver.stg_enrollments` | View; enrollment, latest batch only | 34,996 |
| Silver | `silver.stg_grades` | View; graded enrollment, latest batch only | 34,996 |
| Silver | `silver.stg_attendance` | View; student-course-semester, latest batch only | 34,996 |
| Silver | `silver.student_academic_performance` | Table; one student-semester row | 4,000 |
| Gold | `gold.dim_students` | Table; one row per student | 1,000 |
| Gold | `gold.dim_courses` | Table; one row per course | 10 |
| Gold | `gold.dim_semester` | Table; one row per semester ordinal | 4 |
| Gold | `gold.fact_enrollments` | Table; one row per enrollment | 34,996 |
| Gold | `gold.fact_grades` | Table; one row per graded enrollment | 34,996 |
| Gold | `gold.fact_attendance` | Table; one row per student-course-semester | 34,996 |
| Gold | `gold.student_risk_scores` | Table; latest semester per student | 1,000 |
| Gold | `gold.model_metrics` | Table; one model evaluation run | 1 |

Counts vary with the generated data. Bronze totals accumulate across batches; the table above is per batch/latest snapshot. Every raw table also has `ingestion_batch_id` and `ingested_at`. Both are assigned together across the five CSVs. The dbt `latest_ingestion_batch` macro filters staging views to the most recently ingested batch, leaving prior records in Bronze for history.

The source has integer semester ordinals but no calendar dates, so the warehouse has `dim_semester`, not a fabricated calendar `dim_date`. Table columns and data types are documented in `docs/DATA_DICTIONARY.md`.

## 6. Code And File Map

| Path | Responsibility |
|---|---|
| `docker-compose.yml` | PostgreSQL, dashboard, optional Airflow services, ports, volumes, and environment |
| `Dockerfile` | Python 3.11 app image, installs `requirements.txt`, sets `/workspace` and `PYTHONPATH` |
| `requirements.txt` | Python packages; dbt Core 1.8.8 and dbt-postgres 1.8.2 are deliberately matched |
| `sql/init.sql` | Creates the three database schemas on initial PostgreSQL setup |
| `scripts/generate_data.py` | Writes the five synthetic CSV files under `data/generated/` |
| `src/argus/common/db.py` | Creates the shared SQLAlchemy engine from `DATABASE_URL` |
| `src/argus/etl/ingest.py` | Reads all CSVs, tags a batch, and appends raw tables transactionally |
| `src/argus/quality/validate.py` | Runs SQL checks against Bronze data and fails if any check is nonzero |
| `src/argus/analytics/risk_engine.py` | Builds a logistic-regression model, scores current students, and writes Gold outputs |
| `dashboard/app.py` | Reads risk and performance outputs and renders Streamlit metrics/charts/table |
| `dbt/argus_warehouse/dbt_project.yml` | Declares project, model folders, materializations, and target schemas |
| `dbt/argus_warehouse/profiles.yml` | dbt Postgres connection; host can be set via `DBT_HOST` |
| `dbt/argus_warehouse/models/staging/` | Source-backed, typed Silver views for students/courses/enrollments/grades/attendance |
| `dbt/argus_warehouse/models/marts/` | Student performance aggregate plus Gold dimensions/facts |
| `dbt/argus_warehouse/models/schema.yml` | Source declarations and dbt not-null/unique data tests |
| `dbt/argus_warehouse/macros/latest_ingestion_batch.sql` | Reusable latest-batch filter for staging views |
| `dbt/argus_warehouse/macros/generate_schema_name.sql` | Uses the custom schema exactly (`silver`/`gold`) instead of prefixing it with `public` |
| `dbt/argus_warehouse/tests/student_academic_performance_unique_grain.sql` | Asserts one performance row per student and semester |
| `airflow/dags/argus_pipeline.py` | Optional DAG that chains generation, ingestion, validation, dbt, and risk scoring |
| `tests/test_basic.py` | Verifies core modules import |
| `tests/test_risk_engine.py` | Exercises low- and high-risk scoring cases |
| `.github/workflows/ci.yml` | Installs requirements and runs pytest on pushes and pull requests |
| `.env.example` | Example local `DATABASE_URL` for running Python outside Docker |
| `docs/DATA_DICTIONARY.md` | Warehouse relations, grains, fields, and types |
| `docs/MODEL_CARD.md` | Model purpose, intended use, and governance |
| `docs/SECURITY_AND_PRIVACY.md` | Privacy and security guidance |
| `docs/PROJECT_DOCUMENTATION.md`, `docs/PROJECT_TIMELINE.md` | Project requirements and planned delivery timeline |

Python `__init__.py` files mark the `argus` directories as importable packages. Generated CSVs, model artifacts, Python cache files, and dbt's `target/` output are runtime artifacts, not source modules.

## 7. Important Code Patterns

### Synthetic data generation

In `scripts/generate_data.py`, `RNG = np.random.default_rng(42)` creates a repeatable random-number generator. `ROOT` is derived from the script location, so outputs go to the repository's `data/generated/` regardless of the caller's current directory. The command-line options `--students` and `--semesters` control dataset size; defaults are 1,000 and 4.

Each student receives synthetic identity/cohort fields. The nested student/semester/course loop creates enrollment, grade, and attendance rows. An 8% course skip makes enrollment counts vary; the synthetic course `GST101` is omitted after semester 2. Grades are numeric 0-100 plus a letter grade. Attendance includes percentage and session counts.

### Ingestion and transactions

In `src/argus/etl/ingest.py`, `Path(__file__).resolve().parents[3]` locates the project root from the module file. The code loads all five CSVs before opening the database transaction, then creates one UUID `batch_id` and one UTC `ingested_at` timestamp. The `with engine.begin() as c:` block commits all five appends together or rolls them back if an insert fails. `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` adds batch metadata to older raw tables without deleting their records.

`to_sql(..., if_exists="append")` is intentional: ingestion preserves earlier Bronze batches. Rerunning ingestion without truncating adds another batch. The latest-batch dbt macro ensures downstream views do not combine old and new snapshots.

### Quality checks

`src/argus/quality/validate.py` executes each entry in `CHECKS`. The query returns a count of invalid records; zero prints `PASS`. Nonzero results are accumulated and raised as a `RuntimeError`, which makes the command fail and prevents later pipeline steps when chained with `&&`.

Current checks cover null student IDs, grade and attendance ranges, blank course codes, and enrollments whose course code is missing from the course table. These are Bronze checks; dbt tests additionally check selected columns and uniqueness assumptions in Silver/Gold.

### dbt models and grain

`{{ source('bronze', 'raw_students') }}` tells dbt a model reads an external source relation. `{{ ref('stg_grades') }}` tells dbt to use another model and creates a dependency in the build graph. Staging models cast numeric keys/measures and trim names/codes. The batch macro is appended to every staging query's `FROM` clause.

`student_academic_performance.sql` groups grades by `student_id, semester`; it counts distinct enrollment IDs and counts scores below 50. Attendance is separately averaged at the same student-semester grain before the left join. Aggregating both inputs before joining prevents course-level attendance rows from multiplying the grade summary. A singular dbt test checks that `(student_id, semester)` is unique.

Gold `dim_*` models describe student, course, and semester attributes. `fact_enrollments`, `fact_grades`, and `fact_attendance` retain the source event grains and join to dimensions so unmatched keys are omitted. The dbt build creates these models and runs the configured data tests.

### Risk scoring

In `src/argus/analytics/risk_engine.py`, the four model features are `avg_score`, `attendance_pct`, `failed_courses`, and `courses_taken`. The target uses the following semester's `failed_courses`:

```python
df['next_failed'] = df.groupby('student_id')['failed_courses'].shift(-1).fillna(0).gt(0).astype(int)
```

The final observed semester per student is removed from training because it has no observed next semester. Missing feature values are filled with training medians. A stratified random train/test split and Logistic Regression produce baseline metrics; the model is also saved to `models/risk_model.joblib`.

The composite score combines model probability and three bounded signals:

```text
score = 0.45 * probability
			+ 0.25 * clamp((70 - attendance_pct) / 40, 0, 1)
			+ 0.20 * clamp(failed_courses / 3, 0, 1)
			+ 0.10 * clamp((60 - avg_score) / 40, 0, 1)
```

Scores above 0.60 are `High`, above 0.30 are `Medium`, otherwise `Low`. The output includes reason text based on attendance below 60%, at least two failures, or average score below 50. Recommendations follow simple rules: attendance support, tutoring, performance review, or continued monitoring. Only each student's latest semester is scored. `gold.student_risk_scores` and `gold.model_metrics` are replaced transactionally each run so first-run creation works and repeat runs do not append duplicate results.

### Dashboard

`dashboard/app.py` creates a SQLAlchemy engine from `DATABASE_URL`. Its query joins risk results to `silver.stg_students` (for names/departments) and `silver.student_academic_performance` (for features). Streamlit shows aggregate metrics, risk distribution, attendance-vs-score scatter plot, student selection, risk reasons, and a sorted table. The query is cached for 60 seconds.

## 8. Configuration Reference

| Setting | Default/use |
|---|---|
| `DATABASE_URL` | SQLAlchemy URL; Compose points at `host.docker.internal:5432/argus`; local fallback is `localhost:5432/argus` |
| `DBT_HOST` | dbt profile host; defaults to `host.docker.internal`; override when the Docker host gateway has a different address |
| `POSTGRES_DB` | Compose database name, `argus` |
| `POSTGRES_USER` | Compose database user, `argus` |
| `POSTGRES_PASSWORD` | Compose demo password, `argus` |

For commands run directly on the host instead of in Compose, install `requirements.txt`, set `PYTHONPATH=src`, and provide a host-reachable `DATABASE_URL`. `.env.example` is an example, not an automatically loaded environment file. Do not use the demo credentials for real student information.

## 9. Optional Airflow

The default startup excludes Airflow because metadata initialization is a separate, heavier bootstrap. To start the optional profile:

```bash
docker compose --profile airflow up -d airflow-init airflow-webserver airflow-scheduler
```

Open <http://localhost:8080>. Compose only migrates Airflow metadata; it does not create a web login. Create/configure an account before using or exposing the webserver. The DAG name is `argus_academic_pipeline`; its dependency order is generation -> ingest -> validate -> dbt build -> risk engine. The DAG's dependencies and schedule do not replace the manual quick start above. Airflow is not required to use the dashboard.

## 10. Tests And Validation

```bash
docker compose run --rm dashboard pytest -q
docker compose run --rm dashboard dbt parse --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
docker compose run --rm dashboard dbt build --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
```

`pytest` covers imports and risk-threshold examples. `dbt build` materializes the warehouse and runs 34 current data tests. The most meaningful integration check is the full ordered pipeline in section 3. The CI workflow currently runs pytest, not the Postgres-backed integration pipeline.

## 11. Troubleshooting

| Symptom | Likely cause and response |
|---|---|
| dbt says the Postgres adapter is unsupported | An old or mismatched app image is running. Run `docker compose build dashboard` and `docker compose up -d postgres dashboard`; verify Core 1.8.8 and Postgres adapter 1.8.2 with `dbt --version`. |
| `relation ... does not exist` | A required stage has not run. Check sequence: generate, ingest, validate, dbt build, risk engine. `init.sql` creates schemas, not raw/dbt/risk tables. |
| SQLAlchemy times out connecting to Postgres | Check `docker compose ps`, then test `docker compose exec -T postgres pg_isready -U argus -d argus`. Compose uses the host-gateway alias because nested bridge routing may block direct sibling-container connections. |
| Dashboard says data is unavailable | Run the full pipeline through risk scoring; refresh after the 60-second cache expires. |
| Bronze counts grow after each run | This is expected append-only history. Staging selects the latest batch. Use the targeted TRUNCATE command in section 4 only when you intentionally want a fresh raw dataset. |
| `ModuleNotFoundError: argus` on host | Set `PYTHONPATH=src`, or run commands through the `dashboard` Compose service. |
| `dbt debug` reports Git missing | The app image is intentionally slim and does not include Git. If the Postgres connection test is OK and there are no Git packages in `packages.yml`, this does not prevent the local build. |

## 12. Limitations And Responsible Use

- Synthetic data is useful for exercising the pipeline, not for proving real-world predictive performance.
- Random row splitting can place semesters from the same student in both train and test sets. Metrics may therefore be optimistic; production evaluation should split by student and use temporally separated validation.
- The score thresholds and recommendations are prototype rules, not validated interventions or causal explanations.
- Current input features omit many contextual factors. Do not make high-impact decisions solely from these outputs.
- Production use would require real privacy/security controls, access reviews, secret management, retention policy, audit trails, encryption, model governance, fairness analysis, and human oversight. See `docs/SECURITY_AND_PRIVACY.md` and `docs/MODEL_CARD.md`.
