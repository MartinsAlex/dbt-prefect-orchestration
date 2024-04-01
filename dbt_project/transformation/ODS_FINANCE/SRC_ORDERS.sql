{{ config(materialized='table') }}

select
*
from {{source('yourdatabase', 'orders')}}