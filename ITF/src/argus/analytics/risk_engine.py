from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sqlalchemy import text
from argus.common.db import get_engine

MODEL_DIR = Path('models')
MODEL_DIR.mkdir(exist_ok=True)
FEATURES = ['avg_score', 'attendance_pct', 'failed_courses', 'courses_taken']

def calculate_risk(probability, attendance, failed_courses, avg_score):
    attendance_risk = max(0.0, min(1.0, (70 - attendance) / 40))
    failure_risk = max(0.0, min(1.0, failed_courses / 3))
    performance_risk = max(0.0, min(1.0, (60 - avg_score) / 40))
    score = 0.45 * probability + 0.25 * attendance_risk + 0.20 * failure_risk + 0.10 * performance_risk
    level = 'High' if score > 0.60 else 'Medium' if score > 0.30 else 'Low'
    reasons = []
    if attendance < 60: reasons.append('attendance below 60%')
    if failed_courses >= 2: reasons.append('two or more failed courses')
    if avg_score < 50: reasons.append('average score below 50')
    if not reasons: reasons.append('no major academic warning signal')
    return round(float(score), 4), level, reasons

def main():
    engine = get_engine()
    df = pd.read_sql('select * from silver.student_academic_performance order by student_id, semester', engine)
    df['next_failed'] = df.groupby('student_id')['failed_courses'].shift(-1).fillna(0).gt(0).astype(int)
    train = df[df.groupby('student_id')['semester'].transform('max') != df['semester']].copy()
    X = train[FEATURES].fillna(train[FEATURES].median())
    y = train['next_failed']
    if y.nunique() < 2: raise ValueError('Training data must contain both positive and negative labels.')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    p = model.predict_proba(X_test)[:, 1]
    pred = (p >= 0.5).astype(int)
    metrics = {'accuracy': accuracy_score(y_test, pred), 'precision': precision_score(y_test, pred, zero_division=0), 'recall': recall_score(y_test, pred, zero_division=0), 'f1': f1_score(y_test, pred, zero_division=0), 'roc_auc': roc_auc_score(y_test, p)}
    joblib.dump(model, MODEL_DIR / 'risk_model.joblib')
    current = df.sort_values(['student_id','semester']).groupby('student_id').tail(1).copy()
    current['probability'] = model.predict_proba(current[FEATURES].fillna(X.median()))[:, 1]
    results = []
    for r in current.itertuples():
        score, level, reasons = calculate_risk(r.probability, r.attendance_pct, r.failed_courses, r.avg_score)
        recommendation = 'Attendance intervention' if r.attendance_pct < 60 else 'Academic tutoring' if r.failed_courses >= 2 else 'Performance review' if r.avg_score < 50 else 'Continue monitoring'
        results.append((r.student_id, r.semester, score, level, r.probability, recommendation, '; '.join(reasons)))
    out = pd.DataFrame(results, columns=['student_id','semester','risk_score','risk_level','ml_probability','recommendation','risk_reasons'])
    model_metrics = pd.DataFrame([metrics])
    with engine.begin() as conn:
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS gold'))
        out.to_sql('student_risk_scores', conn, schema='gold', if_exists='replace', index=False)
        model_metrics.to_sql('model_metrics', conn, schema='gold', if_exists='replace', index=False)
    print('Model metrics:', metrics)

if __name__ == '__main__': main()
