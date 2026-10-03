from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "generated"
RNG = np.random.default_rng(42)

COURSES = [
    ("CSC101","Introduction to Computing",3),
    ("CSC201","Data Structures",3),
    ("CSC203","Database Systems",3),
    ("CSC205","Computer Networks",3),
    ("CSC207","Operating Systems",3),
    ("CSC301","Data Engineering",3),
    ("CSC303","Software Engineering",3),
    ("CSC305","Artificial Intelligence",3),
    ("MTH201","Statistics",3),
    ("GST101","Communication Skills",2),
]

def main(n=1000, semesters=4):
    OUT.mkdir(parents=True, exist_ok=True)
    departments = ["Computer Science","Information Technology","Software Engineering","Information Systems"]

    students = pd.DataFrame([
        {
            "student_id": f"STU{i:05d}",
            "first_name": f"Student{i:05d}",
            "last_name": "Synthetic",
            "department": RNG.choice(departments),
            "entry_year": int(RNG.choice([2022,2023,2024]))
        } for i in range(1,n+1)
    ])
    courses = pd.DataFrame(COURSES, columns=["course_code","course_name","credit_units"])

    enrollments, grades, attendance = [], [], []

    for _, s in students.iterrows():
        ability = np.clip(RNG.normal(.68,.14), .25,.95)
        base_att = np.clip(RNG.normal(.84,.09), .45,.98)

        for sem in range(1,semesters+1):
            decline = max(0, sem-2) * RNG.uniform(0,.08)
            for _, c in courses.iterrows():
                if c.course_code == "GST101" and sem > 2:
                    continue
                if RNG.random() < .08:
                    continue

                eid = f"{s.student_id}_{sem}_{c.course_code}"
                enrollments.append([eid,s.student_id,c.course_code,sem])

                score = np.clip(100*(ability-RNG.uniform(0,.18)+RNG.normal(0,.10)),0,100)
                if RNG.random() < .12 and sem >= 3:
                    score = np.clip(score-RNG.uniform(10,30),0,100)

                grade = "A" if score>=70 else "B" if score>=60 else "C" if score>=50 else "D" if score>=45 else "F"
                grades.append([eid,s.student_id,c.course_code,sem,round(float(score),2),grade])

                att = np.clip(base_att-decline+RNG.normal(0,.07),.30,1)
                attendance.append([s.student_id,c.course_code,sem,round(float(att*100),2),14,int(round(att*14))])

    pd.DataFrame(students).to_csv(OUT/"students.csv",index=False)
    courses.to_csv(OUT/"courses.csv",index=False)
    pd.DataFrame(enrollments,columns=["enrollment_id","student_id","course_code","semester"]).to_csv(OUT/"enrollments.csv",index=False)
    pd.DataFrame(grades,columns=["enrollment_id","student_id","course_code","semester","score","grade"]).to_csv(OUT/"grades.csv",index=False)
    pd.DataFrame(attendance,columns=["student_id","course_code","semester","attendance_pct","classes_held","classes_attended"]).to_csv(OUT/"attendance.csv",index=False)
    print(f"Generated {n} students in {OUT}")

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--students",type=int,default=1000)
    p.add_argument("--semesters",type=int,default=4)
    a=p.parse_args()
    main(a.students,a.semesters)
