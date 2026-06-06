
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select clv_segment
from "warehouse"."main_gold"."gold_customer_lifetime_value"
where clv_segment is null



  
  
      
    ) dbt_internal_test