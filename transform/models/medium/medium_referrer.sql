with medium as (select to_json("raw_data") as raw_data_json, type from good_content_analytics_input_stage.medium),

final as (
    select
        CAST(json_extract_path_text(raw_data_json, 'postId') as VARCHAR) as postId,
        CAST(json_extract_path_text(raw_data_json, 'type') as VARCHAR) as type,
        CAST(json_extract_path_text(raw_data_json, 'totalCount') as NUMERIC) as totalCount
    from medium
    where type = 'referrer'
)

select *
from final
