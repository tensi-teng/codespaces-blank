select enrollment_id, student_id, course_code,
       cast(semester as integer) semester
from {{ source('bronze','raw_enrollments') }}
{{ latest_ingestion_batch('bronze','raw_enrollments') }}