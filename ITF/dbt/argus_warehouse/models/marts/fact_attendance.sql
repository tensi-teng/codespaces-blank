select a.student_id, a.course_code, a.semester,
       a.attendance_pct, a.classes_held, a.classes_attended
from {{ ref('stg_attendance') }} a
inner join {{ ref('dim_students') }} s using (student_id)
inner join {{ ref('dim_courses') }} c using (course_code)
inner join {{ ref('dim_semester') }} d using (semester)