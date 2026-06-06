
    
    



select _ingested_at
from "warehouse"."main_bronze"."bronze_customers"
where _ingested_at is null


