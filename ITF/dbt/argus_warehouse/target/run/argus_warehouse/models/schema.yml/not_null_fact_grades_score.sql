select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select score
from "argus"."gold"."fact_grades"
where score is null



      
    ) dbt_internal_test