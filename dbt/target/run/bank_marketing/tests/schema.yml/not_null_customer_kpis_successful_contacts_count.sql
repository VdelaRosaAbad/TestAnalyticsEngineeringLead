
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select successful_contacts_count
from `generated-surf-468214-g1`.`bank_marketing_dm`.`customer_kpis`
where successful_contacts_count is null



  
  
      
    ) dbt_internal_test