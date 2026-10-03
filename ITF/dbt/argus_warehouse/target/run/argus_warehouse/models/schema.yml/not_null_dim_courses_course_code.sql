select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select course_code
from "argus"."gold"."dim_courses"
where course_code is null



      
    ) dbt_internal_test