with grade_summary as (
    select student_id, semester, avg(score) avg_score,
           count(distinct enrollment_id) courses_taken,
           sum(case when score < 50 then 1 else 0 end) failed_courses
    from "argus"."silver"."stg_grades"
    group by student_id, semester
), attendance as (
    select student_id, semester, avg(attendance_pct) attendance_pct
    from "argus"."silver"."stg_attendance"
    group by student_id, semester
)
select g.student_id, g.semester, round(g.avg_score,2) avg_score,
       g.courses_taken, g.failed_courses, a.attendance_pct
from grade_summary g left join attendance a using(student_id, semester)