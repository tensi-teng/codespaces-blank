select trim(course_code) course_code,
       trim(course_name) course_name,
       cast(credit_units as integer) credit_units
from "argus"."bronze"."raw_courses"
where ingestion_batch_id = (
    select ingestion_batch_id
    from "argus"."bronze"."raw_courses"
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)