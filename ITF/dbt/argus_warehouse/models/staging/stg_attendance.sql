select student_id, course_code, cast(semester as integer) semester,
    cast(attendance_pct as numeric(5,2)) attendance_pct,
    cast(classes_held as integer) classes_held,
    cast(classes_attended as integer) classes_attended
from {{ source('bronze','raw_attendance') }}
{{ latest_ingestion_batch('bronze','raw_attendance') }}
