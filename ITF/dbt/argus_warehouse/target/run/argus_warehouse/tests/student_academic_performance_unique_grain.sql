select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      select student_id, semester
from "argus"."silver"."student_academic_performance"
group by student_id, semester
having count(*) > 1
      
    ) dbt_internal_test