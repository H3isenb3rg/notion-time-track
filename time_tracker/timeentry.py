from dataclasses import dataclass, field

from .bucket import Bucket


@dataclass
class TimeEntry:
    id: str = field()
    bucket_area: str = field()
    bucket_id: str = field()
    is_sentric: bool = field()
    last_week: bool = field()
    current_week: bool = field()
    times: tuple[str, str] = field()
    hours: float = field()
    name: str = field()


def get_boolean(raw_entry, property) -> bool:
    return raw_entry["properties"][property]["formula"]["boolean"]


def get_times(raw_entry):
    date = raw_entry["properties"]["Start Time"]["date"]
    return (date["start"], date["end"])


def parse_time_entry(raw_entry):
    _id: str = raw_entry["id"]
    properties = raw_entry["properties"]
    bucket_area: str = properties["Bucket Area"]["rollup"]["array"][0]["select"]["name"]
    bucket_id: str = properties["Bucket"]["relation"][0]["id"]
    is_sentric: bool = get_boolean(raw_entry, "Is Sentric")
    last_week: bool = get_boolean(raw_entry, "Last Week")
    current_week: bool = get_boolean(raw_entry, "Current Week")
    times: tuple[str, str] = get_times(raw_entry)
    hours: float = properties["Hours"]["formula"]["number"]
    name: str = properties["Name"]["title"][0]["plain_text"]

    return TimeEntry(_id, bucket_area, bucket_id, is_sentric, last_week, current_week, times, hours, name)


def build_db_page(description: str, bucket: Bucket, times: list[str], db_id: str):
    parent = {"type": "database_id", "database_id": db_id}
    properties = {"Name": _build_name(description), "Bucket": _build_bucket(bucket.id), "Start Time": _build_start_time(times[0], times[1])}

    return {"parent": parent, "properties": properties}


def _build_name(page_name: str) -> dict:
    return {"type": "title", "title": [{"type": "text", "text": {"content": page_name}}]}


def _build_start_time(start_time: str, end_time: str) -> dict:
    return {"type": "date", "date": {"start": start_time, "end": end_time, "time_zone": None}}


def _build_bucket(bucket_id: str):
    return {"type": "relation", "relation": [{"id": bucket_id}], "has_more": False}
