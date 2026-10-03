select enrollment_id, student_id, course_code,
       cast(semester as integer) semester,
       cast(score as numeric(5,2)) score, grade
from {{ source('bronze','raw_grades') }}
{{ latest_ingestion_batch('bronze','raw_grades') }}
