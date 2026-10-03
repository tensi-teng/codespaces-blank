# ARGUS Model Card

**Model:** Logistic Regression baseline  
**Purpose:** Estimate probability of a failed course in the following semester from academic-history features.  
**Features:** average score, attendance, failed-course count, courses taken.

### Intended Use
Academic monitoring and prioritization of human review.

### Prohibited Use
Clinical/mental-health assessment, automated discipline, admissions decisions, scholarship eligibility or irreversible student decisions.

### Limitations
Synthetic development data cannot establish production validity. Real deployment requires institutional validation, calibration and subgroup performance analysis.

### Monitoring
Track precision, recall, F1, ROC-AUC, calibration, drift and subgroup performance.
