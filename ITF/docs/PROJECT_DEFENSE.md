# ARGUS Project Defense Guide

## Project At A Glance

**Project:** ARGUS — Academic Risk & Guidance Analytics System  
**Category:** Data engineering, analytics, and decision support  
**Primary users:** Authorized academic advisors and support personnel  
**Current status:** Working prototype demonstrated with synthetic data

### Short Pitch

ARGUS is a reproducible academic-data pipeline and dashboard. It combines grades and attendance into student-semester indicators, estimates the probability of a subsequent failed semester with a baseline Logistic Regression model, and presents the results with observable warning signals for human review. It is a decision-support prototype, not an automated student decision system.

## Problem And Rationale

Academic records are often stored across separate student, course, grade, enrollment, and attendance datasets. Reviewing many records manually can be repetitive, difficult to reproduce, and inconsistent across reviewers. This can make it harder for support staff to prioritize which records deserve timely human attention.

ARGUS demonstrates a technical response to that problem: standardize the input, check basic data quality, transform it into a consistent analytical grain, calculate risk indicators, and display the result with the underlying factors.

The project does **not** claim that institutions lack existing student-information systems, that the prototype connects to a real institutional system, or that its synthetic model has proven it improves student outcomes. Its value is the demonstrated data workflow and the explainable human-review pattern.

## Aim And Objectives

**Aim:** Build a reproducible prototype that turns academic source records into reviewable academic-support indicators.

Objectives:

- Generate or ingest student, course, enrollment, grade, and attendance records.
- Preserve raw inputs in a Bronze PostgreSQL layer with ingestion-batch metadata.
- Validate required IDs, value ranges, and course references before modeling.
- Use dbt to create typed staging views, student-semester measures, and Gold dimensions/facts.
- Train and evaluate a baseline model for a clearly defined next-semester outcome.
- Show risk levels, recommendations, and observable reasons in a Streamlit dashboard.
- Keep people responsible for interpreting and acting on the indicators.

## Scope

Implemented in this prototype:

- Synthetic data generation for 1,000 students, 10 courses, and four semesters by default.
- Append-only Bronze ingestion, batch tracking, and latest-batch staging.
- SQL quality validation and dbt data tests.
- Silver student-semester performance table and Gold dimensions, facts, risk scores, and model metrics.
- Logistic Regression baseline, deterministic composite risk score, and rule-based explanations/recommendations.
- Streamlit dashboard for institution-level summaries and individual-record review.
- Optional Airflow DAG; the core demonstration can run without Airflow.

Not implemented or not established:

- Connection to a real student-information system or production-grade access control.
- Real calendar dates, interventions, case management, alerts, or advisor feedback loops.
- Validated causal effects, production model accuracy, calibration, or fairness across student groups.
- Automated decisions about discipline, admissions, funding, or student eligibility.

## How The System Works

```text
Synthetic CSV files
        |
        v
Python ingestion -- shared batch ID and timestamp
        |
        v
PostgreSQL Bronze -- append-only raw_* tables
        |
        +--> SQL data-quality validation
        |
        v
dbt Silver -- latest-batch staging views and student-semester table
        |
        +--> dbt Gold dimensions and academic facts
        |
        v
Risk engine -- next-semester model and composite indicators
        |
        v
Gold risk outputs --> Streamlit dashboard --> human review
```

Technologies and their roles:

| Technology | Role in ARGUS |
|---|---|
| Docker Compose | Starts PostgreSQL and the dashboard runtime; Airflow is optional |
| PostgreSQL | Stores raw and transformed records |
| Python/pandas | Generates, loads, validates, and scores data |
| dbt-postgres | Builds SQL models and executes data tests |
| scikit-learn | Trains/evaluates the Logistic Regression baseline |
| Streamlit/Plotly | Presents summaries, charts, and student-level factors |
| Apache Airflow | Optional scheduling/orchestration of the pipeline |

## Data Design

The main analytical grain is **one student in one semester**. Course-level grade and attendance records are aggregated before they are combined, preventing one student-semester from appearing multiple times in the risk model input.

| Layer | Examples | Purpose |
|---|---|---|
| Bronze | `raw_students`, `raw_courses`, `raw_enrollments`, `raw_grades`, `raw_attendance` | Preserve source-shaped rows and ingestion history |
| Silver | `stg_*`, `student_academic_performance` | Type/trim source fields and calculate one row per student-semester |
| Gold | `dim_students`, `dim_courses`, `dim_semester`, `fact_*` | Curated analytical dimensions and event-grain facts |
| Gold outputs | `student_risk_scores`, `model_metrics` | Latest student risk results and evaluation metrics |

Bronze ingestion is append-only. Every CSV load has one shared `ingestion_batch_id` and `ingested_at`; dbt staging reads the newest batch. This supports reproducible reruns while retaining prior raw batches. A clean demo reset truncates the five Bronze raw tables but preserves the PostgreSQL volume and schemas.

The generated source has semester ordinals but no calendar dates. The warehouse therefore uses `dim_semester`; a calendar date dimension would require dated source data.

## Risk Method

### Prediction Target

For each student-semester, the model target is whether the student's **next observed semester** has one or more courses with scores below 50. The final observed semester for each student is omitted from training because its next-semester result is unknown.

### Features

- Average course score in the semester.
- Average attendance percentage in the semester.
- Number of failed courses (score below 50).
- Number of graded courses taken.

The baseline is scikit-learn Logistic Regression. Training and test records are split randomly with stratification and a fixed random state. This is suitable for a reproducible prototype, but semesters from the same student can appear in both sets; reported metrics can therefore be optimistic. A production evaluation should split by student and/or time.

### Composite Score

The displayed score combines predicted probability with bounded academic signals:

```text
score = 0.45 * next-failure probability
      + 0.25 * clamp((70 - attendance percentage) / 40, 0, 1)
      + 0.20 * clamp(failed courses / 3, 0, 1)
      + 0.10 * clamp((60 - average score) / 40, 0, 1)
```

#### What The Formula Means

Each input is converted to a value between 0 and 1 before weighting. `clamp(x, 0, 1)` means values below 0 become 0 and values above 1 become 1. This keeps unusually low or high values from making any one component exceed its intended range.

| Component | How to read it | Behavior |
|---|---|---|
| `next-failure probability` | The Logistic Regression estimate that the student will have at least one failing course in the next observed semester. | Already between 0 and 1. It contributes the largest weight, 45%, because forecasting the defined target is the model's primary signal. It is a probability estimate, not a certainty. |
| `clamp((70 - attendance) / 40, 0, 1)` | A linearly increasing attendance concern below 70%. | At 70% or above, this term is 0; at 50% it is 0.5; at 30% or below it is 1. Its weight is 25%. |
| `clamp(failed courses / 3, 0, 1)` | A linearly increasing signal for current-semester course failures. | Zero failures gives 0; one gives about 0.33; two gives about 0.67; three or more gives 1. Its weight is 20%. |
| `clamp((60 - average score) / 40, 0, 1)` | A linearly increasing low-score signal below an average of 60. | At 60 or above, this term is 0; at 40 it is 0.5; at 20 or below it is 1. Its weight is 10%. |

Because every component is in `[0, 1]` and the weights (0.45 + 0.25 + 0.20 + 0.10) sum to 1, the composite score also stays in `[0, 1]`. The weights let the score combine a forward-looking estimate with direct, observable current-semester indicators. They are hand-set prototype weights, not coefficients learned from outcomes, and have not been validated with advisors or real institutional data.

#### Worked Example

For an illustrative student with a 0.80 model probability, 50% attendance, two failed courses, and an average score of 45:

```text
0.45 * 0.80                  = 0.3600
0.25 * ((70 - 50) / 40)     = 0.1250
0.20 * (2 / 3)               = 0.1333
0.10 * ((60 - 45) / 40)     = 0.0375
                                        ------
Composite score              = 0.6558
```

This is classified as `High` because it is greater than 0.60. The displayed rules would also report low attendance, two or more failed courses, and average score below 50. The example explains the arithmetic only; it is not a real student's result.

Levels are `High` above 0.60, `Medium` above 0.30 through 0.60, and `Low` at or below 0.30. The dashboard also displays rule-based reasons: attendance below 60%, two or more failed courses, and average score below 50. Recommendations are simple prototype rules, not model-generated treatment plans.

The reason thresholds are intentionally separate from the continuous score terms. For example, attendance between 60% and 70% increases the score component but does not trigger the `attendance below 60%` reason; one failure contributes to the score but does not trigger the two-failure reason. Therefore, reason text is a short list of configured flags, not a complete decomposition of every score contribution. Recommendation selection also has precedence: attendance below 60% first, then two or more failures, then average score below 50, otherwise continued monitoring.

## Demonstration Plan

Suggested 5-7 minute walkthrough:

1. State the problem and emphasize that the prototype supports human review rather than making decisions.
2. Show the architecture and the Bronze/Silver/Gold data flow.
3. Run or show the pipeline commands from `docs/TECHNICAL_DOCUMENTATION.md`.
4. Show the validation output and dbt build/test summary.
5. Open the dashboard at `http://localhost:8501`; explain aggregate counts and risk distribution.
6. Select a student and connect the displayed risk level to the score, attendance, failures, and reason text.
7. Close with limitations: synthetic data, baseline evaluation, and need for human oversight.

If running the demo live, start services and execute these sequentially from the project directory:

```bash
docker compose up --build -d postgres dashboard
docker compose run --rm dashboard python scripts/generate_data.py
docker compose run --rm dashboard python -m argus.etl.ingest
docker compose run --rm dashboard python -m argus.quality.validate
docker compose run --rm dashboard dbt build --project-dir /workspace/dbt/argus_warehouse --profiles-dir /workspace/dbt/argus_warehouse
docker compose run --rm dashboard python -m argus.analytics.risk_engine
```

Airflow is optional and should not be started during a short defense unless orchestration itself is being demonstrated. The Compose profile does not automatically create an Airflow web login.

## Demonstration Results

One verified default synthetic run produced:

- 1,000 students, 10 courses, and 34,996 enrollments/grades/attendance rows per latest batch.
- 4,000 student-semester performance rows and 1,000 latest-semester risk rows.
- Five Bronze quality checks passing.
- 46 dbt models/data tests passing.
- Three Python tests passing.
- A dashboard health response of HTTP 200.

The recorded model metrics for that synthetic run were approximately:

| Metric | Value |
|---|---:|
| Accuracy | 0.837 |
| Precision | 0.872 |
| Recall | 0.918 |
| F1 | 0.894 |
| ROC-AUC | 0.899 |

These metrics describe one generated dataset and the current random row split only. They are **not** evidence of real-world accuracy or expected institutional performance. Re-run the pipeline before a defense if presenting live metrics, and explain the evaluation limitation rather than presenting the values as validated claims.

## Likely Questions And Suggested Answers

### What problem does ARGUS solve?

It demonstrates how to make multi-file academic records easier to validate, aggregate, and review consistently. It prioritizes records with observable signals; it does not replace existing student systems or advisors.

### Why use Bronze, Silver, and Gold?

Bronze keeps source-shaped history, Silver standardizes and aggregates it at a defined grain, and Gold provides curated facts, dimensions, and risk outputs. This separates ingestion concerns from analytical and presentation needs.

### Why Logistic Regression?

It is a simple, inspectable baseline for a binary outcome and produces probabilities. It is a starting point for evaluation, not a claim that it is the best model. More complex models should only be considered after data quality, leakage-safe evaluation, calibration, and governance are addressed.

### How are explanations generated?

The output includes explicit threshold-based reasons from attendance, failures, and average score. These are observable signals, not causal explanations of why an outcome occurred.

### Can the model be trusted to identify at-risk students?

Not for consequential use yet. It was demonstrated on synthetic data, and the current row-based split can leak student-specific patterns across train and test. Real deployment requires representative data, student/time-separated validation, calibration, subgroup evaluation, privacy controls, and human review.

### Why does the dashboard show the latest semester only?

The model scores each student's most recent observed semester for current review. Earlier semesters supply the training sequence and remain available in the analytical performance table.

### What happens when a quality check fails?

The validator reports nonzero invalid counts and exits with an error. When pipeline commands are chained with `&&`, later steps do not run, preventing invalid source data from silently becoming risk outputs.

### What would be the next development steps?

1. Replace synthetic records with a governed, privacy-reviewed integration and define access/retention controls.
2. Add student-grouped and time-based evaluation, probability calibration, fairness analysis, and model monitoring.
3. Gather advisor feedback and validate that the outputs are useful and do not create harmful false positives or false negatives.
4. Add dated source fields if a true calendar dimension and time-aware analysis are required.
5. Harden orchestration, secret handling, deployment, audit logging, and operational monitoring before production.

## Responsible-Use Position

ARGUS must not be used for autonomous discipline, admissions, scholarship eligibility, mental-health assessment, or irreversible student decisions. A risk label is a prompt for qualified human review, not a finding about a student's character, motivation, or future. The synthetic demo credentials and local Compose setup are not production security controls.

## Related Project Documents

- `docs/TECHNICAL_DOCUMENTATION.md` - setup, commands, code explanations, troubleshooting.
- `docs/DATA_DICTIONARY.md` - table grains, columns, and data types.
- `docs/PROJECT_DOCUMENTATION.md` - requirements, objectives, and users.
- `docs/MODEL_CARD.md` - model purpose, intended use, and limitations.
- `docs/SECURITY_AND_PRIVACY.md` - privacy and security requirements.