import requests, json

from .config import ConfigClass

class NotionAPI:
    def __init__(self, configuration: ConfigClass) -> None:
        self.config = configuration

    def retrieve_hours(self):
        response = requests.post(self.config.time_entries_query_url, json=self.config.payload_curr_last_week, headers=self.config.headers)
        json_obj = json.loads(response.text)
        curr_week_hours = sum(float(record["properties"]["Hours"]["formula"]["number"]) for record in json_obj["results"] if record["properties"]["Current Week"]["formula"]["boolean"])
        last_week_hours = sum(float(record["properties"]["Hours"]["formula"]["number"]) for record in json_obj["results"] if record["properties"]["Last Week"]["formula"]["boolean"])

        return curr_week_hours, last_week_hours

    def build_db_page(self, description: str, bucket: str, times: list[str]):
        parent = {
            "type": "database_id",
            "database_id": self.config.db_id
        }
        
        properties = {
            "Name": self._build_name(description),
            "Bucket": self._build_bucket(self.config.allowed_buckets[bucket]),
            "Start Time": self._build_start_time(times[0], times[1])
        }

        return {
            "parent": parent,
            "properties": properties
        }

    def send_time_entry(self, db_page):
        response = requests.post(self.config.new_page_url, json=db_page, headers=self.config.headers)
        response.raise_for_status()
        

    def _build_name(self, page_name: str) -> dict:
        return {
            "type": "title",
            "title": [
                {
                "type": "text",
                "text": {
                    "content": page_name
                }
                }
            ]
            }

    def _build_start_time(self, start_time: str, end_time: str) -> dict:
        return {
            "type": "date",
            "date": {
                "start": start_time,
                "end": end_time,
                "time_zone": None
            }
            }

    def _build_bucket(self, bucket_id: str):
        return {
            "type": "relation",
            "relation": [
                {
                "id": bucket_id
                }
            ],
            "has_more": False
        }