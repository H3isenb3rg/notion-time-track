from dataclasses import dataclass, field


@dataclass
class ConfigClass():
    weekly_hours: int = field(default=10)
    db_id: str = field(default="061a26b964d041c397e0b323220c6e8c")
    time_entries_query_url: str = field(
        default="https://api.notion.com/v1/databases/061a26b964d041c397e0b323220c6e8c/query")
    new_page_url: str = field(default="https://api.notion.com/v1/pages")

    def __post_init__(self):
        token = open("notionAPItoken.txt", "r").readline()
        oauth_token = f"Bearer {token}"
        self.headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "authorization": oauth_token
        }

        curr_last_week_sentric_filter = {
            "and": [
                {
                    "property": "Is Sentric",
                    "formula": {
                        "checkbox": {
                            "equals": True
                        }
                    }
                }, {
                    "or": [
                        {
                            "property": "Last Week",
                            "formula": {
                                "checkbox": {
                                    "equals": True
                                }
                            }
                        },
                        {
                            "property": "Current Week",
                            "formula": {
                                "checkbox": {
                                    "equals": True
                                }
                            }
                        }
                    ]
                }
            ]
        }
        self.payload_curr_last_week = {"page_size": 100,
                                       "filter": curr_last_week_sentric_filter}

        self.allowed_buckets = {
            "casper": "bbc55b52-cbd2-4388-8882-65031a8f3fe5",
            "various": "2cdbc31b-d2d4-4f64-af57-7be9318394c5"
        }
