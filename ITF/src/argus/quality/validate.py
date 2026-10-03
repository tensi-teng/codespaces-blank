import os
from sqlalchemy import create_engine, text

URL=os.getenv('DATABASE_URL','postgresql+psycopg2://argus:argus@localhost:5432/argus')
CHECKS={
 'student_id_required':'SELECT COUNT(*) FROM bronze.raw_students WHERE student_id IS NULL',
 'score_range':'SELECT COUNT(*) FROM bronze.raw_grades WHERE score < 0 OR score > 100',
 'attendance_range':'SELECT COUNT(*) FROM bronze.raw_attendance WHERE attendance_pct < 0 OR attendance_pct > 100',
 'course_code_required':"SELECT COUNT(*) FROM bronze.raw_courses WHERE course_code IS NULL OR TRIM(course_code)=''",
 'orphan_course_codes':'''SELECT COUNT(*) FROM bronze.raw_enrollments e LEFT JOIN bronze.raw_courses c USING(course_code) WHERE c.course_code IS NULL'''
}

def validate():
    engine=create_engine(URL, pool_pre_ping=True)
    failures=[]
    with engine.connect() as c:
        for name,q in CHECKS.items():
            n=c.execute(text(q)).scalar()
            print(name, 'PASS' if n==0 else 'FAIL', n)
            if n!=0: failures.append((name,n))
    if failures: raise RuntimeError(failures)
    return True

def main(): validate()

if __name__=='__main__': main()
