import requests, json, re, datetime

weekly_hours = 10
token = open("notionAPItoken.txt", "r").readline()
db_id = open("db_id.txt", "r").readline()
db_query_url = f"https://api.notion.com/v1/databases/{db_id}/query"
new_page_url = "https://api.notion.com/v1/pages"
oauth_token = f"Bearer {token}"
last_week_sentric_filter =  {
            "and": [
                {
                    "property": "Is Sentric",
                    "formula": {
                        "checkbox": {
                        "equals": True
                        }
                    }
                },
                {
                    "property": "Last Week",
                    "formula": {
                        "checkbox": {
                        "equals": True
                        }
                    }
                }
            ]
        }

current_week_sentric_filter =  {
            "and": [
                {
                    "property": "Is Sentric",
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
payload_query = {"page_size": 100, "filter": current_week_sentric_filter}
payload_last_week = {"page_size": 100, "filter": last_week_sentric_filter}
headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "authorization": oauth_token
}
allowed_buckets = {
    "casper": "bbc55b52-cbd2-4388-8882-65031a8f3fe5",
    "various": "2cdbc31b-d2d4-4f64-af57-7be9318394c5"
}

def run():
    # TODO: same request for curr and last week.
    # Get current week times
    response = requests.post(db_query_url, json=payload_query, headers=headers)
    json_obj = json.loads(response.text)
    hours = count_hours(json_obj["results"])
    print(f"Current week hours -> {hours}")

    # Get last week times
    response = requests.post(db_query_url, json=payload_last_week, headers=headers)
    json_obj = json.loads(response.text)
    last_week_hours = count_hours(json_obj["results"])
    if last_week_hours<weekly_hours:
        diff = weekly_hours - last_week_hours
        print(f"Hours from last week -> {diff}")
    else:
        diff = 0

    print(f"Remaining hours -> {weekly_hours + diff - hours}")

    # Get new time entry
    parsed_input = get_input_dict()
    db_page = build_db_page(parsed_input)
    print(json.dumps(parsed_input, indent=2))
    response = input("Confirm Data? (Y/N)\n> ")
    if response.strip().lower() == "n":
        run()

    # Send POST request with new time entry
    response = requests.post(new_page_url, json=db_page, headers=headers)
    response.raise_for_status()
    
    

def count_hours(json_data):
    hours = 0
    for record in json_data:
        hours += float(record["properties"]["Hours"]["formula"]["number"])

    return hours

def get_bucket() -> str:
    while True:
        try:
            bucket = re.findall(r"\s*(\S+)\s*", input("Insert Bucket\n> "))[0]
            if bucket.lower() in allowed_buckets.keys():
                return bucket
            else:
                print("Illegal Bucket")
                continue
        except IndexError as err:
            pass

def get_description() -> str:
    while True:
        try:
            return re.findall(r"\s*(\S+.*\S+)\s*", input("Insert Short Description\n> "))[0]
        except IndexError as err:
            pass

def build_time(raw_time):
    hours = int(raw_time[0])
    minutes = int(raw_time[1]) if raw_time[1]!="" else 0
    return datetime.time(hours, minutes)

def today_with_time(time: datetime.time) -> datetime.datetime:
    today = datetime.date.today()
    return datetime.datetime(
        today.year, today.month, today.day, time.hour, time.minute, time.second
    )

def get_times() -> tuple[datetime.time, datetime.time]:
    while True:
        try:
            raw_times = re.findall(r"\s*([01]?[0-9]|2[0-3])[:\.]?(\d{1,2})?\s*", input("Insert Start and End Times\n> "))
            if len(raw_times)<2:
                print("Missing time stamp")
                continue

            start_time = build_time(raw_times[0])
            end_time = build_time(raw_times[1])
            if start_time == end_time:
                print(f"Same time for start and end found: {start_time}")
                continue
            
            if start_time > end_time:
                tmp = start_time
                start_time = end_time
                end_time = tmp
            
            break
        except IndexError as err:
            pass

    return today_with_time(start_time).isoformat(), today_with_time(end_time).isoformat()

def build_name(page_name: str) -> dict:
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

def build_start_time(start_time: str, end_time: str) -> dict:
    return {
          "id": f"XEO%5E",
          "type": "date",
          "date": {
            "start": start_time,
            "end": end_time,
            "time_zone": None
          }
        }

def build_bucket(bucket_name):
    return {
        "type": "relation",
        "relation": [
            {
              "id": allowed_buckets[bucket_name]
            }
        ],
        "has_more": False
    }

def build_db_page(input_object):
    parent = {
        "type": "database_id",
        "database_id": db_id
      }
    
    properties = {
        "Name": build_name(input_object["description"]),
        "Bucket": build_bucket(input_object["bucket"]),
        "Start Time": build_start_time(input_object["dates"][0], input_object["dates"][1])
    }

    return {
        "parent": parent,
        "properties": properties
    }
    

def get_input_dict() -> dict:
    bucket = get_bucket().lower()
    description = get_description()
    start, end = get_times()

    return {
        "bucket": bucket,
        "description": description,
        "dates": [start, end]
    }