{{ config(materialized='table') }}

select
    *
from
    {{ ref('SRC_HR_LOGS') }}
where department = 'Finance'