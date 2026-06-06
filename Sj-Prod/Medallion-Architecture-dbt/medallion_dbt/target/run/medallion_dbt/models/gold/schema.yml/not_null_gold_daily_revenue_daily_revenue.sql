
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select daily_revenue
from "warehouse"."main_gold"."gold_daily_revenue"
where daily_revenue is null



  
  
      
    ) dbt_internal_test