
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_revenue
from "warehouse"."main_gold"."gold_product_performance"
where total_revenue is null



  
  
      
    ) dbt_internal_test