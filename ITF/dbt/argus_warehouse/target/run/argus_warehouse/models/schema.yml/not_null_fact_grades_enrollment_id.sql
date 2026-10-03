select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select enrollment_id
from "argus"."gold"."fact_grades"
where enrollment_id is null



      
    ) dbt_internal_test