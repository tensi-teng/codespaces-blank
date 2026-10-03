select course_code, course_name, credit_units
from {{ ref('stg_courses') }}