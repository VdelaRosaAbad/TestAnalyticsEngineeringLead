
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select customer_id
from `generated-surf-468214-g1`.`bank_marketing_dm`.`customer_kpis`
where customer_id is null



  
  
      
    ) dbt_internal_test