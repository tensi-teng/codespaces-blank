
  
    

  create  table "argus"."gold"."dim_courses__dbt_tmp"
  
  
    as
  
  (
    select course_code, course_name, credit_units
from "argus"."silver"."stg_courses"
  );
  