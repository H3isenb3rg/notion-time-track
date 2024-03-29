import pathlib


DEFAULT_CONFIG = {
    "weekly_hours": 10,
    "buckets_db_id": "f3f7e9cd21a74436b8912632ec6dadf6",
    "buckets_query_url": "https://api.notion.com/v1/databases/f3f7e9cd21a74436b8912632ec6dadf6/query",
    "time_entries_db_id": "061a26b964d041c397e0b323220c6e8c",
    "time_entries_query_url": "https://api.notion.com/v1/databases/061a26b964d041c397e0b323220c6e8c/query",
    "new_page_url": "https://api.notion.com/v1/pages",
    "bucket_area": None
}

try:
    NOTION_API_TOKEN = pathlib.Path("notionAPItoken.txt").read_text()
except FileNotFoundError:
    print("API token file(notionAPItoken.txt) not found!")
    NOTION_API_TOKEN = None
