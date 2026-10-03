{% macro latest_ingestion_batch(source_name, table_name) -%}
where ingestion_batch_id = (
    select ingestion_batch_id
    from {{ source(source_name, table_name) }}
    where ingestion_batch_id is not null
    order by ingested_at desc
    limit 1
)
{%- endmacro %}