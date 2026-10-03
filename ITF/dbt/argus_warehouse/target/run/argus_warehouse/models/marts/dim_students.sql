
  
    

  create  table "argus"."gold"."dim_students__dbt_tmp"
  
  
    as
  
  (
    select student_id, first_name, last_name,
       concat_ws(' ', first_name, last_name) full_name,
       department, entry_year
from "argus"."silver"."stg_students"
  );
  