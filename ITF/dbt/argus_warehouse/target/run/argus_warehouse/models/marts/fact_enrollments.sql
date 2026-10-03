
  
    

  create  table "argus"."gold"."fact_enrollments__dbt_tmp"
  
  
    as
  
  (
    select e.enrollment_id, e.student_id, e.course_code, e.semester
from "argus"."silver"."stg_enrollments" e
inner join "argus"."gold"."dim_students" s using (student_id)
inner join "argus"."gold"."dim_courses" c using (course_code)
inner join "argus"."gold"."dim_semester" d using (semester)
  );
  