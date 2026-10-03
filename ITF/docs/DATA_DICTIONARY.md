# ARGUS Data Dictionary

## Bronze

| Table | Grain | Contents |
|---|---|---|
| `bronze.raw_students` | Student per ingestion batch | Identity, department, and entry year |
| `bronze.raw_courses` | Course per ingestion batch | Course name and credit units |
| `bronze.raw_enrollments` | Enrollment per ingestion batch | Student, course, and semester keys |
| `bronze.raw_grades` | Enrollment grade per ingestion batch | Score and letter grade |
| `bronze.raw_attendance` | Student-course-semester per ingestion batch | Attendance percentage and class counts |

All raw tables include `ingestion_batch_id TEXT` and `ingested_at TIMESTAMPTZ`. A batch ID is shared across all five files. Ingestion appends new batches; staging models consume only the most recent batch.

## Silver

| Model | Grain | Output |
|---|---|---|
| `silver.stg_students` | Student | Trimmed names, department, entry year |
| `silver.stg_courses` | Course | Trimmed course code/name and integer credit units |
| `silver.stg_enrollments` | Enrollment | Enrollment keys and integer semester |
| `silver.stg_grades` | Enrollment grade | Enrollment keys, numeric score, letter grade |
| `silver.stg_attendance` | Student-course-semester | Numeric attendance percentage and class counts |
| `silver.student_academic_performance` | Student-semester | Average score, courses taken, failed courses, average attendance |

## Gold

| Table | Grain | Contents |
|---|---|---|
| `gold.dim_students` | Student | Student attributes and display name |
| `gold.dim_courses` | Course | Course attributes |
| `gold.dim_semester` | Semester number | The available synthetic semester ordinal |
| `gold.fact_enrollments` | Enrollment | Student, course, and semester keys |
| `gold.fact_grades` | Enrollment grade | Keys, score, and letter grade |
| `gold.fact_attendance` | Student-course-semester | Keys, attendance percentage, classes held/attended |
| `gold.student_risk_scores` | Student's latest semester | Risk score, level, probability, recommendation, reasons |
| `gold.model_metrics` | Model run | Accuracy, precision, recall, F1, and ROC-AUC |

The generated data provides semester numbers but no calendar dates. `dim_semester` is therefore an ordinal dimension; a calendar `dim_date` needs dated source data.

## Field Types

| Field | Database type | Description |
|---|---|---|
| `student_id` | TEXT | Synthetic student identifier |
| `enrollment_id` | TEXT | Synthetic enrollment identifier |
| `course_code` | TEXT | Course identifier |
| `semester` | INTEGER | Synthetic semester ordinal |
| `entry_year` | INTEGER | Student entry cohort |
| `score` | NUMERIC(5,2) | Course score from 0 to 100 |
| `attendance_pct` | NUMERIC(5,2) | Attendance percentage from 0 to 100 |
| `classes_held` | INTEGER | Number of course sessions held |
| `classes_attended` | INTEGER | Number of course sessions attended |
| `avg_score` | NUMERIC | Mean course score per student-semester |
| `courses_taken` | INTEGER | Number of graded enrollments in the semester |
| `failed_courses` | INTEGER | Scores below 50 in the semester |
| `risk_score` | DOUBLE PRECISION | Composite academic monitoring score |
| `risk_level` | TEXT | Low, Medium, or High |
| `ml_probability` | DOUBLE PRECISION | Predicted next-semester failure probability |
| `recommendation` | TEXT | Support-oriented action |
| `risk_reasons` | TEXT | Observable factors supporting the flag |
| `ingestion_batch_id` | TEXT | Shared identifier for one CSV ingestion batch |
| `ingested_at` | TIMESTAMPTZ | UTC time when the batch was loaded |