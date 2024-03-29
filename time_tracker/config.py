from dataclasses import dataclass, field, asdict
import pathlib, toml, appdirs

from . import constants


CFG_LOC = pathlib.Path(appdirs.site_config_dir(appname="time_tracker", appauthor="H3isenb3rg")) / "config.toml"


@dataclass
class ConfigClass:
    weekly_hours: int = field(default=10)
    buckets_db_id: str = field(default="f3f7e9cd21a74436b8912632ec6dadf6")
    buckets_query_url: str = field(default="https://api.notion.com/v1/databases/f3f7e9cd21a74436b8912632ec6dadf6/query")
    time_entries_db_id: str = field(default="061a26b964d041c397e0b323220c6e8c")
    time_entries_query_url: str = field(default="https://api.notion.com/v1/databases/061a26b964d041c397e0b323220c6e8c/query")
    new_page_url: str = field(default="https://api.notion.com/v1/pages")
    bucket_area: str | None = field(default=None)

    def dict(self):
        return asdict(self)

    def __post_init__(self):
        token = constants.NOTION_API_TOKEN
        oauth_token = f"Bearer {token}"
        self.headers = {"accept": "application/json", "Notion-Version": "2022-06-28", "content-type": "application/json", "authorization": oauth_token}

        sentric_buckets_filter = {"property": "Area", "select": {"equals": self.bucket_area}}
        self.payload_sentric_buckets = {"page_size": 100, "filter": sentric_buckets_filter} if self.bucket_area is not None else {"page_size": 100}

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

    def __str__(self) -> str:
        config_dict = self.dict()
        return "\n".join(f"{key}: {config_dict[key]}" for key in config_dict)


def load_config():
    if not CFG_LOC.exists():
        CFG_LOC.parent.mkdir(parents=True, exist_ok=True)
        with open(CFG_LOC, "w") as f:
            toml.dump(constants.DEFAULT_CONFIG, f)
        print(f"Initialized new default config at {CFG_LOC}.")

    return ConfigClass(**toml.load(CFG_LOC))
