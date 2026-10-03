select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select enrollment_id
from "argus"."silver"."stg_enrollments"
where enrollment_id is null



      
    ) dbt_internal_test