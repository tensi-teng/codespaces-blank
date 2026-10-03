select student_id, trim(first_name) first_name, trim(last_name) last_name,
       department, entry_year
from {{ source('bronze','raw_students') }}
{{ latest_ingestion_batch('bronze','raw_students') }}
