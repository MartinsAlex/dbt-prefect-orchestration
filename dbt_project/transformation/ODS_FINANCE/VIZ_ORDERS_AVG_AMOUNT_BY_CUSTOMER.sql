{{ config(materialized='table') }}

select 
    name as customer_name,
    sum(order_amount)
from {{ ref('VIZ_ORDERS') }}
group by
    name
