
    
    

select
    order_date as unique_field,
    count(*) as n_records

from "warehouse"."main_gold"."gold_daily_revenue"
where order_date is not null
group by order_date
having count(*) > 1


