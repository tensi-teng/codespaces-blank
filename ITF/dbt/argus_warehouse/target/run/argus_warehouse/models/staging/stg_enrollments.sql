
  create view "argus"."silver"."stg_enrollments__dbt_tmp"
    
    
  as (
    select enrollment_id, student_id, course_code,
       cast(semester as integer) semester
from "argus"."bronze"."raw_enrollments"
where ingestion_batch_id = (
    select ingestion_batch_id
    from "argus"."bronze"."raw_enrollments"
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)
  );