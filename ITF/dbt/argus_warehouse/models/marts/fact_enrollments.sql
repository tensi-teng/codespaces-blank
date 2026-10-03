select e.enrollment_id, e.student_id, e.course_code, e.semester
from {{ ref('stg_enrollments') }} e
inner join {{ ref('dim_students') }} s using (student_id)
inner join {{ ref('dim_courses') }} c using (course_code)
inner join {{ ref('dim_semester') }} d using (semester)