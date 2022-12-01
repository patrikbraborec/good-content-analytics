from medium import StatGrabberPublication
from datetime import datetime
import os
import psycopg2
import json

# Local testing
from dotenv import load_dotenv
load_dotenv()

start = datetime(year=2020, month=1, day=1)
stop = datetime.now()
publication = StatGrabberPublication(slug=os.environ["MEDIUM_PUBLICATION"],
                                     sid=os.environ["MEDIUM_SID"],
                                     uid=os.environ["MEDIUM_UID"],
                                     start=start,
                                     stop=stop)

overview_data = publication.get_all_story_overview()
post_ids = set(record["postId"] for record in overview_data)

all_story_stats = publication.get_all_story_stats(post_ids)

with psycopg2.connect(host=os.environ["DB_HOST"], database=os.environ["DB_NAME"],
                      user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"]) as conn:
    with conn.cursor() as cursor:
        for record in overview_data:
            cursor.execute(
                "INSERT INTO good_content_analytics_input_stage.medium (raw_data, type, date) VALUES(%s, %s, %s)",
                (json.dumps(record), "overview", stop))
        for story_stat in all_story_stats["data"]["post"]:
            for referrer in story_stat["referrers"]:
                cursor.execute(
                    "INSERT INTO good_content_analytics_input_stage.medium (raw_data, type, date) VALUES(%s, %s, %s)",
                    (json.dumps(referrer), "referrer", stop))
        conn.commit()
