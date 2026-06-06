
    
    

with all_values as (

    select
        tier as value_field,
        count(*) as n_records

    from "warehouse"."main_silver"."silver_customers"
    group by tier

)

select *
from all_values
where value_field not in (
    'BRONZE','SILVER','GOLD'
)


