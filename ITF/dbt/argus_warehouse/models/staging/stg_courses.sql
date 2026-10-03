select trim(course_code) course_code,
       trim(course_name) course_name,
       cast(credit_units as integer) credit_units
from {{ source('bronze','raw_courses') }}
{{ latest_ingestion_batch('bronze','raw_courses') }}