
    
    

select
    customer_id as unique_field,
    count(*) as n_records

from "warehouse"."main_gold"."gold_customer_lifetime_value"
where customer_id is not null
group by customer_id
having count(*) > 1


