
    
    

select
    course_code as unique_field,
    count(*) as n_records

from "argus"."gold"."dim_courses"
where course_code is not null
group by course_code
having count(*) > 1


