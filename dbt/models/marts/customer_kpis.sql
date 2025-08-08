{{ config(materialized='table') }}

with base as (
    select * from {{ ref('stg_bank_marketing') }}
)

, agg as (
    select
        customer_id,
        sum(case when converted = 1 then 1 else 0 end) as successful_contacts_count,
        count(*) as total_contacts,
        safe_divide(sum(case when converted = 1 then 1 else 0 end), count(*)) as conversion_rate,
        case
            when age < 30 then 'young'
            when age between 30 and 50 then 'adult'
            else 'senior'
        end as customer_segment
    from base
    group by customer_id, customer_segment
)

select
    customer_id,
    successful_contacts_count,
    total_contacts,
    conversion_rate,
    customer_segment
from agg

