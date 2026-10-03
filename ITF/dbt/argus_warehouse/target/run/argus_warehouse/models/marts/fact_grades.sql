
  
    

  create  table "argus"."gold"."fact_grades__dbt_tmp"
  
  
    as
  
  (
    select g.enrollment_id, g.student_id, g.course_code, g.semester,
       g.score, g.grade
from "argus"."silver"."stg_grades" g
inner join "argus"."gold"."fact_enrollments" e using (enrollment_id)
  );
  