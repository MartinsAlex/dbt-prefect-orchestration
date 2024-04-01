{{ config(materialized='table') }}

select
    orders.*,
    customers.name,
    customers.email,
    accounts.account_number,
    accounts.balance
from
    {{ ref("SRC_ORDERS") }} orders
left join
    {{ source('yourdatabase', 'accounts') }} accounts ON (accounts.account_id =  orders.account_id)
left join
    {{ source('yourdatabase', 'customers') }} customers ON (customers.customer_id =  accounts.customer_id)
