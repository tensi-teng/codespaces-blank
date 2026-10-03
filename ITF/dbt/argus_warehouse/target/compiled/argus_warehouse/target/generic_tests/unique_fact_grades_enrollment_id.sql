
    
    

select
    enrollment_id as unique_field,
    count(*) as n_records

from "argus"."gold"."fact_grades"
where enrollment_id is not null
group by enrollment_id
having count(*) > 1


