

  create or replace view `generated-surf-468214-g1`.`bank_marketing_dm`.`stg_bank_marketing`
  OPTIONS()
  as 

with source as (
    select *
    from `generated-surf-468214-g1`.bank_marketing_raw.bank_marketing
)

, cleaned as (
    select
        cast(row_number() over(order by (select 1)) as int64) as customer_id,
        age,
        job,
        marital,
        education,
        `default`,
        housing,
        loan,
        contact,
        month,
        day_of_week,
        duration,
        campaign,
        pdays,
        previous,
        poutcome,
        emp_var_rate,
        cons_price_idx,
        cons_conf_idx,
        euribor3m,
        nr_employed,
        case when lower(y) in ('yes','y','1','true','t') then 1 else 0 end as converted
    from source
)

select * from cleaned;

