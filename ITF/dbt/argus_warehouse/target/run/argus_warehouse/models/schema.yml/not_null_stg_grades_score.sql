select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select score
from "argus"."silver"."stg_grades"
where score is null



      
    ) dbt_internal_test