import requests, json
from typing import Iterable

from .config import ConfigClass
from .timeentry import TimeEntry, parse_time_entry
from .bucket import Bucket, parse_bucket


class NotionAPI:
    def __init__(self, configuration: ConfigClass) -> None:
        self.config = configuration
        self.buckets = self._get_sentric_buckets()

    def retrieve_hours(self):
        time_entries = self._get_curr_last_week()
        curr_week_hours = self._sum_hours(filter(lambda x: x.current_week, time_entries))
        last_week_hours = self._sum_hours(filter(lambda x: x.last_week, time_entries))
        return curr_week_hours, last_week_hours

    def build_recap(self) -> dict[str, Iterable[TimeEntry]]:
        time_entries = self._get_curr_last_week()
        return {"Current Week": filter(lambda x: x.current_week, time_entries), "Last Week": filter(lambda x: x.last_week, time_entries)}

    def _week_recap(self, week: str, entries: list[TimeEntry]) -> str:
        if len(entries) <= 0:
            return week + "\n\tNo Time entries\n"

        recap = f"{week} ({self._sum_hours(entries)}h)\n"
        for entry in entries:
            recap += f"\t{entry}\n"
        return recap

    def send_time_entry(self, db_page):
        self._post_request(self.config.new_page_url, db_page, self.config.headers)

    def _get_curr_last_week(self):
        raw_entries = self._post_request(self.config.time_entries_query_url, self.config.payload_curr_last_week, self.config.headers)["results"]
        return [parse_time_entry(entry, self.buckets) for entry in raw_entries]

    def _sum_hours(self, entries_list: Iterable[TimeEntry]):
        return sum(float(entry.hours) for entry in entries_list)

    def _post_request(self, url: str, json_payload: dict, headers: dict):
        response = requests.post(url, json=json_payload, headers=headers, timeout=5)
        response.raise_for_status()
        return json.loads(response.text)

    def _get_sentric_buckets(self) -> list[Bucket]:
        json_obj = self._post_request(self.config.buckets_query_url, self.config.payload_sentric_buckets, self.config.headers)["results"]
        return sorted([parse_bucket(page) for page in json_obj], key=lambda b: b.area)

    def _build_name(self, page_name: str) -> dict:
        return {"type": "title", "title": [{"type": "text", "text": {"content": page_name}}]}

    def _build_start_time(self, start_time: str, end_time: str) -> dict:
        return {"type": "date", "date": {"start": start_time, "end": end_time, "time_zone": None}}

    def _build_bucket(self, bucket_id: str):
        return {"type": "relation", "relation": [{"id": bucket_id}], "has_more": False}
