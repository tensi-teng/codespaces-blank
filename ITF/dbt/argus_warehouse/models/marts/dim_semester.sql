select semester from {{ ref('stg_enrollments') }}
group by semester