select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select semester
from "argus"."silver"."student_academic_performance"
where semester is null



      
    ) dbt_internal_test