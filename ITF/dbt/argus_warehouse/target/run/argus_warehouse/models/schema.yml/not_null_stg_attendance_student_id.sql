select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select student_id
from "argus"."silver"."stg_attendance"
where student_id is null



      
    ) dbt_internal_test