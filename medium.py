from datetime import datetime, timezone
import requests
import json
from medium_constants import stats_post_ref_q


def convert_datetime_to_unix(dt: datetime, ms: bool = True):
    dt = dt.astimezone(timezone.utc)
    dt = int(dt.timestamp())
    if ms:
        dt = dt * 1000
    return dt


class StatGrabberBase:
    def __init__(self, sid: str, uid: str, start: datetime, stop: datetime):

        for s in [start, stop]:
            if not isinstance(s, datetime):
                msg = f'argument "{s}" must be of type datetime.datetime'
                raise TypeError(msg)

        self.start_unix, self.stop_unix = map(convert_datetime_to_unix, (start, stop))
        self.sid = sid
        self.uid = uid
        self.cookies = {"sid": sid, "uid": uid}
        self._setup_requests()

    def _setup_requests(self):

        s = requests.Session()
        s.headers.update({"content-type": "application/json", "accept": "application/json"})

        cookies = requests.utils.cookiejar_from_dict(self.cookies)
        s.cookies = cookies
        self.session = s

    def _fetch(self, url, params=None):

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response

    @staticmethod
    def _decode_json(response):
        cleaned = response.text.replace("])}while(1);</x>", "")
        return json.loads(cleaned)["payload"]

    def get_story_stats(self, post_id: str):

        gql_endpoint = "https://medium.com/_/graphql"

        post_data = {"variables": {"postId": post_id}}
        post_data["operationName"] = "StatsPostReferrersContainer"
        post_data["query"] = stats_post_ref_q

        r = self.session.post(gql_endpoint, json=post_data)

        return r.json()

    def get_all_story_stats(self, post_ids):

        container = {"data": {"post": []}}

        for post in post_ids:
            data = self.get_story_stats(post)
            container["data"]["post"] += [data["data"]["post"]]

        return container


class StatGrabberUser(StatGrabberBase):
    """
    u = StatGrabberUser("","","",datetime(year=2020, month=1, day=1), datetime.now())
    u.get_summary_stats()
    """

    def __init__(self, username: str, sid: str, uid: str, start: datetime, stop: datetime):

        self.username = str(username)
        self.slug = str(username)
        super().__init__(sid, uid, start, stop)
        self.stats_url = f"https://medium.com/@{username}/stats"
        self.totals_endpoint = f"https://medium.com/@{username}/stats/total/{self.start_unix}/{self.stop_unix}"

    def __repr__(self):
        return f"username: {self.username} // uid: {self.uid}"

    def get_summary_stats(self, events=False, limit=50, **kwargs):
        params = {"filter": "not-response", "limit": limit, **kwargs}
        if events:
            response = self._fetch(self.totals_endpoint)
        else:
            response = self._fetch(self.stats_url, params=params)

        data = self._decode_json(response)

        if data.get("paging", {}).get("next"):
            next_cursor_idx = data["paging"]["next"]["to"]
            next_page = self.get_summary_stats(limit=limit, to=next_cursor_idx)
            data["value"].extend(next_page)

        return data["value"]


class StatGrabberPublication(StatGrabberBase):
    def __init__(self, slug, sid, uid, start, stop):

        url = f"https://medium.com/{slug}"
        self.url = url
        super().__init__(sid, uid, start, stop)
        homepage = self._fetch(self.url)
        # TODO figure out why requests lib doesn't get full html from this url
        data = self._decode_json(homepage)
        self.attrs_json = data["collection"]
        self._unpack_attrs(self.attrs_json)

        collections_endpoint = f"https://medium.com/_/api/collections/{self.id}/stats/"
        timeframe = f"?from={self.start_unix}&to={self.stop_unix}"
        create_endpoint = lambda x: collections_endpoint + x + timeframe
        self.views_endpoint = create_endpoint("views")
        self.visitors_endpoint = create_endpoint("visitors")

    # TODO - create a helper classmethod that takes in a URL and extracts slug

    def _unpack_attrs(self, attrs_json):

        self.id = self.attrs_json["id"]
        self.slug = self.attrs_json["slug"]
        self.name = self.attrs_json["name"]
        self.creator = self.attrs_json["creatorId"]
        self.description = self.attrs_json["description"]
        try:
            self.domain = self.attrs_json["domain"]
        except:
            self.domain = None

    def __repr__(self):
        return f"{self.name} - {self.description}"

    def get_events(self, type_="views"):
        if type_ == "views":
            response = self._fetch(self.views_endpoint)
        elif type_ == "visitors":
            response = self._fetch(self.visitors_endpoint)
        else:
            raise ValueError('"type_" param must be either "views" or "visitors"')

        data = self._decode_json(response)

        return data["value"]

    def get_all_story_overview(self, limit: int = 50, **kwargs):
        params = {"limit": limit, **kwargs}
        endpoint = f"https://medium.com/{self.slug}/stats/stories"
        response = self._fetch(endpoint, params)

        data = self._decode_json(response)
        if data.get("paging", {}).get("next"):
            next_cursor_idx = data["paging"]["next"]["to"]
            next_page = self.get_all_story_overview(limit=limit, to=next_cursor_idx)
            data["value"].extend(next_page)

        return data["value"]
