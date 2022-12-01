with medium as (select to_json("raw_data") as raw_data_json from good_content_analytics_input_stage.medium),

final as (
    select
        CAST(json_extract_path_text(raw_data_json, 'postId') as VARCHAR) as postId,
        CAST(json_extract_path_text(raw_data_json, 'title') as VARCHAR) as title,
        CAST(json_extract_path_text(raw_data_json, 'claps') as INTEGER) as claps,
        CAST(json_extract_path_text(raw_data_json, 'reads') as INTEGER) as reads,
        CAST(json_extract_path_text(raw_data_json, 'views') as INTEGER) as views
    from medium
)

select *
from final
