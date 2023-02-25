from dataclasses import dataclass, field


@dataclass
class ConfigClass:
    weekly_hours: int = field(default=10)
    buckets_db_id: str = field(default="f3f7e9cd21a74436b8912632ec6dadf6")
    buckets_query_url: str = field(default="https://api.notion.com/v1/databases/f3f7e9cd21a74436b8912632ec6dadf6/query")
    time_entries_db_id: str = field(default="061a26b964d041c397e0b323220c6e8c")
    time_entries_query_url: str = field(default="https://api.notion.com/v1/databases/061a26b964d041c397e0b323220c6e8c/query")
    new_page_url: str = field(default="https://api.notion.com/v1/pages")
    api_token: str | None = field(default=None)

    def __post_init__(self):
        token = open("notionAPItoken.txt", "r").readline() if self.api_token is None else self.api_token
        oauth_token = f"Bearer {token}"
        self.headers = {"accept": "application/json", "Notion-Version": "2022-06-28", "content-type": "application/json", "authorization": oauth_token}

        sentric_buckets_filter = {"property": "Area", "select": {"equals": "Sentric"}}
        self.payload_sentric_buckets = {"page_size": 100, "filter": sentric_buckets_filter}

        curr_last_week_sentric_filter = {
            "and": [
                {"property": "Is Sentric", "formula": {"checkbox": {"equals": True}}},
                {
                    "or": [
                        {"property": "Last Week", "formula": {"checkbox": {"equals": True}}},
                        {"property": "Current Week", "formula": {"checkbox": {"equals": True}}},
                    ]
                },
            ]
        }
        self.payload_curr_last_week = {"page_size": 100, "filter": curr_last_week_sentric_filter}
