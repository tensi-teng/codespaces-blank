select a.student_id, a.course_code, a.semester,
       a.attendance_pct, a.classes_held, a.classes_attended
from "argus"."silver"."stg_attendance" a
inner join "argus"."gold"."dim_students" s using (student_id)
inner join "argus"."gold"."dim_courses" c using (course_code)
inner join "argus"."gold"."dim_semester" d using (semester)