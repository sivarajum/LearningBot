
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select tier
from "warehouse"."main_silver"."silver_customers"
where tier is null



  
  
      
    ) dbt_internal_test