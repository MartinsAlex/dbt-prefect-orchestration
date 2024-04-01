{{ config(materialized='table') }}

select
    orders.*
from
    {{ref('F_ORDERS')}} orders
left join {{ref("VIZ_HR_FINANCE_EMPLOYEE")}} on 1=1
