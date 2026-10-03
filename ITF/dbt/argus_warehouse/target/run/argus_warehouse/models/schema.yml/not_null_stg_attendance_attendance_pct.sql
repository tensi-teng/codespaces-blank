select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select attendance_pct
from "argus"."silver"."stg_attendance"
where attendance_pct is null



      
    ) dbt_internal_test