
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select lifetime_value
from "warehouse"."main_gold"."gold_customer_lifetime_value"
where lifetime_value is null



  
  
      
    ) dbt_internal_test