select student_id, semester
from {{ ref('student_academic_performance') }}
group by student_id, semester
having count(*) > 1