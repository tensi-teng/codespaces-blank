select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select
    semester as unique_field,
    count(*) as n_records

from "argus"."gold"."dim_semester"
where semester is not null
group by semester
having count(*) > 1



      
    ) dbt_internal_test