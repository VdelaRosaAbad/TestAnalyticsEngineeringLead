
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
select
  conversion_rate as value
from `generated-surf-468214-g1`.`bank_marketing_dm`.`customer_kpis`
where (conversion_rate < 0) or (conversion_rate > 1)

  
  
      
    ) dbt_internal_test