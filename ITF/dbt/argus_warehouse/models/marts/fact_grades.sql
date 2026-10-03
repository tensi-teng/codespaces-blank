select g.enrollment_id, g.student_id, g.course_code, g.semester,
       g.score, g.grade
from {{ ref('stg_grades') }} g
inner join {{ ref('fact_enrollments') }} e using (enrollment_id)