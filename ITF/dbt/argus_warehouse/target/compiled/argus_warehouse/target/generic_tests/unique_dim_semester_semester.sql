
    
    

select
    semester as unique_field,
    count(*) as n_records

from "argus"."gold"."dim_semester"
where semester is not null
group by semester
having count(*) > 1


