select
    *
from {{source('yourdatabase', 'purchaseorders')}}
left join {{ref("VIZ_HR_FINANCE_EMPLOYEE")}} on 1=1