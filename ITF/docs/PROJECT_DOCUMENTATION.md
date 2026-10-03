# ARGUS Project Documentation

## 1. Executive Summary
ARGUS (Academic Risk & Guidance Analytics System) automates the processing of academic records so authorized academic-support personnel can identify observable academic warning signals more efficiently.

## 2. Problem Statement
Manual review of large academic-record volumes can be repetitive and inconsistent. ARGUS provides a repeatable data pipeline that converts records into analytical indicators and human-readable support signals.

## 3. Objectives
- Build a reproducible academic-data pipeline.
- Implement Bronze/Silver/Gold storage.
- Enforce data-quality controls.
- Orchestrate processing with Airflow.
- Build and evaluate a baseline predictive model.
- Provide an explainable dashboard.
- Demonstrate responsible handling of student data.

## 4. Functional Requirements
FR-01 ingest students, courses, enrollments, grades and attendance.  
FR-02 validate required data constraints.  
FR-03 produce student-semester analytical metrics.  
FR-04 calculate academic-risk indicators.  
FR-05 provide explanations for flagged records.  
FR-06 visualize institutional and student-level results.  
FR-07 orchestrate the end-to-end workflow.  
FR-08 provide automated tests.

## 5. Non-Functional Requirements
Reproducibility, maintainability, configurability, testability, explainability, privacy-awareness and reasonable performance for moderate academic datasets.

## 6. Users
**Counselor/Advisor:** reviews academic signals.  
**Data Engineer/Administrator:** operates the pipeline.  
**Reviewer:** evaluates engineering and analytical quality.

## 7. Evaluation
Report actual model metrics, data-quality failures detected, pipeline runtime, scaling behavior and dashboard responsiveness. Do not claim target accuracy before experiments are run.

## 8. Ethical Position
ARGUS is decision support, not autonomous counseling. It must not be used for disciplinary or clinical decisions. Human review remains mandatory.

## 9. Deliverables
Source code, Docker environment, PostgreSQL warehouse, dbt project, Airflow DAG, risk model, dashboard, tests, technical documentation, evaluation report and final academic report.
