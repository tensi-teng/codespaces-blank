select student_id, trim(first_name) first_name, trim(last_name) last_name,
       department, entry_year
from "argus"."bronze"."raw_students"
where ingestion_batch_id = (
    select ingestion_batch_id
    from "argus"."bronze"."raw_students"
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)