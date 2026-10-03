select student_id, semester
from "argus"."silver"."student_academic_performance"
group by student_id, semester
having count(*) > 1