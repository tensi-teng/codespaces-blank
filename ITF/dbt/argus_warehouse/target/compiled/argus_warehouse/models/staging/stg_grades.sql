select enrollment_id, student_id, course_code,
       cast(semester as integer) semester,
       cast(score as numeric(5,2)) score, grade
from "argus"."bronze"."raw_grades"
where ingestion_batch_id = (
    select ingestion_batch_id
    from "argus"."bronze"."raw_grades"
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)