
  
    

  create  table "argus"."gold"."dim_semester__dbt_tmp"
  
  
    as
  
  (
    select semester from "argus"."silver"."stg_enrollments"
group by semester
  );
  