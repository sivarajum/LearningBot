
    
    

with all_values as (

    select
        clv_segment as value_field,
        count(*) as n_records

    from "warehouse"."main_gold"."gold_customer_lifetime_value"
    group by clv_segment

)

select *
from all_values
where value_field not in (
    'high_value','mid_value','low_value'
)


