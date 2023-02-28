from dataclasses import dataclass, field
import requests, json

from .config import ConfigClass


@dataclass
class Bucket:
    id: str = field()
    name: str = field()
    area: str = field()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, str):
            return __o.lower() == self.name.lower()

        if isinstance(__o, Bucket):
            return __o.name.lower() == self.name.lower()

        raise TypeError(f"Object of type {type(__o)} can't be compared with a Bucket")

    def __str__(self) -> str:
        return f"{self.name} ({self.area})"


class NotionAPI:
    def __init__(self, configuration: ConfigClass) -> None:
        self.config = configuration
        self.buckets = self._get_sentric_buckets()

    def retrieve_hours(self):
        json_obj = self._post_request(self.config.time_entries_query_url, self.config.payload_curr_last_week, self.config.headers)
        curr_week_hours = self._count_week_hours(json_obj["results"])
        last_week_hours = self._count_week_hours(json_obj["results"], curr_week=False)
        return curr_week_hours, last_week_hours

    def build_db_page(self, description: str, bucket: Bucket, times: list[str]):
        parent = {"type": "database_id", "database_id": self.config.time_entries_db_id}

        properties = {"Name": self._build_name(description), "Bucket": self._build_bucket(bucket.id), "Start Time": self._build_start_time(times[0], times[1])}

        return {"parent": parent, "properties": properties}

    def send_time_entry(self, db_page):
        self._post_request(self.config.new_page_url, db_page, self.config.headers)

    def _count_week_hours(self, results_list, curr_week: bool = True):
        week = "Current Week" if curr_week else "Last Week"
        return sum(float(record["properties"]["Hours"]["formula"]["number"]) for record in results_list if record["properties"][week]["formula"]["boolean"])

    def _post_request(self, url: str, json_payload: dict, headers: dict):
        response = requests.post(url, json=json_payload, headers=headers)
        response.raise_for_status()
        return json.loads(response.text)

    def _get_sentric_buckets(self) -> list[Bucket]:
        json_obj = self._post_request(self.config.buckets_query_url, self.config.payload_sentric_buckets, self.config.headers)

        return sorted([
            Bucket(page["id"], page["properties"]["Name"]["title"][0]["plain_text"], page["properties"]["Area"]["select"]["name"])
            for page in json_obj["results"]
        ], key=lambda b: b.area)

    def _build_name(self, page_name: str) -> dict:
        return {"type": "title", "title": [{"type": "text", "text": {"content": page_name}}]}

    def _build_start_time(self, start_time: str, end_time: str) -> dict:
        return {"type": "date", "date": {"start": start_time, "end": end_time, "time_zone": None}}

    def _build_bucket(self, bucket_id: str):
        return {"type": "relation", "relation": [{"id": bucket_id}], "has_more": False}
