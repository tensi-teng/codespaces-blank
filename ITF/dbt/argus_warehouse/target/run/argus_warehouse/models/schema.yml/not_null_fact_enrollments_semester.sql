select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select semester
from "argus"."gold"."fact_enrollments"
where semester is null



      
    ) dbt_internal_test