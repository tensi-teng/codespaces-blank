select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    course_code as unique_field,
    count(*) as n_records

from "argus"."silver"."stg_courses"
where course_code is not null
group by course_code
having count(*) > 1



      
    ) dbt_internal_test