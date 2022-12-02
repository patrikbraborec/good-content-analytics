with medium as (select to_json("raw_data") as raw_data_json, type from good_content_analytics_input_stage.medium),

final as (
    select
        CAST(json_extract_path_text(raw_data_json, 'postId') as VARCHAR) as postId,
        CAST(json_extract_path_text(raw_data_json, 'title') as VARCHAR) as title,
        CAST(json_extract_path_text(raw_data_json, 'claps') as NUMERIC) as claps,
        CAST(json_extract_path_text(raw_data_json, 'reads') as NUMERIC) as reads,
        CAST(json_extract_path_text(raw_data_json, 'views') as NUMERIC) as views
    from medium
    where type = 'overview'
)

select *
from final