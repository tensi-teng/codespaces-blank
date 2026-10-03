select student_id, course_code, cast(semester as integer) semester,
    cast(attendance_pct as numeric(5,2)) attendance_pct,
    cast(classes_held as integer) classes_held,
    cast(classes_attended as integer) classes_attended
from "argus"."bronze"."raw_attendance"
where ingestion_batch_id = (
    select ingestion_batch_id
    from "argus"."bronze"."raw_attendance"
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)