
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_age_days
from "warehouse"."main_silver"."silver_customers"
where customer_age_days is null



  
  
      
    ) dbt_internal_test