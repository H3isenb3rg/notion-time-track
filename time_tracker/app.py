import requests, json, re, datetime
from .config import ConfigClass
    

def run(configuration: ConfigClass):
    # Get current week times
    response = requests.post(configuration.time_entries_query_url, json=configuration.payload_curr_last_week, headers=configuration.headers)
    json_obj = json.loads(response.text)
    curr_week_hours = sum(float(record["properties"]["Hours"]["formula"]["number"]) for record in json_obj["results"] if record["properties"]["Current Week"]["formula"]["boolean"])
    last_week_hours = sum(float(record["properties"]["Hours"]["formula"]["number"]) for record in json_obj["results"] if record["properties"]["Last Week"]["formula"]["boolean"])
    print(f"Current week hours -> {curr_week_hours}")
    
    diff = configuration.weekly_hours - last_week_hours if last_week_hours<configuration.weekly_hours else 0
    if diff>0:
        print(f"Hours from last week -> {diff}")

    print(f"Remaining hours -> {configuration.weekly_hours + diff - curr_week_hours}")

    # Get new time entry
    parsed_input = get_input_dict(configuration.allowed_buckets)
    db_page = build_db_page(
        configuration.db_id, 
        parsed_input["description"], 
        configuration.allowed_buckets[parsed_input["bucket"]],
        parsed_input["dates"]
        )
    print(json.dumps(parsed_input, indent=2))
    response = input("Confirm Data? (Y/N)\n> ")
    if response.strip().lower() == "n":
        run(configuration)

    # Send POST request with new time entry
    response = requests.post(configuration.new_page_url, json=db_page, headers=configuration.headers)
    response.raise_for_status()

    print("New time entry successfully added!")
    run(configuration)
    
    

def count_hours(json_data):
    hours = 0
    for record in json_data:
        hours += float(record["properties"]["Hours"]["formula"]["number"])

    return hours

def get_bucket(allowed_buckets: dict[str, str]) -> str:
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

def get_times() -> tuple[str, str]:
    while True:
        try:
            raw_input = input("Insert Start and End Times\n> ")
            raw_times = re.findall(r"\s*(\d{1,2})[:\.]?(\d{2})?\s*", raw_input)
            #raw_times.extend(re.findall(r"\s*(1\d{1})[:\.]?(\d{1,2})?\s*", raw_input))
            #raw_times.extend(re.findall(r"\s*(2[0-3])[:\.]?(\d{1,2})?\s*", raw_input))
            if len(raw_times)<2:
                print("Missing time stamp")
                continue

            try:
                start_time = build_time(raw_times[0])
                end_time = build_time(raw_times[1])
            except ValueError:
                print("Wrong Time values. Insert valid 24h times")
                continue
                
            if start_time == end_time:
                print(f"Same time for start and end found: {start_time}")
                continue
            
            if start_time > end_time:
                tmp = start_time
                start_time = end_time
                end_time = tmp
            
            break
        except IndexError:
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

def build_bucket(bucket_id: str):
    return {
        "type": "relation",
        "relation": [
            {
              "id": bucket_id
            }
        ],
        "has_more": False
    }

def build_db_page(db_id: str, description: str, bucket_id: str, times: list):
    parent = {
        "type": "database_id",
        "database_id": db_id
      }
    
    properties = {
        "Name": build_name(description),
        "Bucket": build_bucket(bucket_id),
        "Start Time": build_start_time(times[0], times[1])
    }

    return {
        "parent": parent,
        "properties": properties
    }
    

def get_input_dict(allowed_buckets: dict[str, str]) -> dict:
    bucket = get_bucket(allowed_buckets).lower()
    description = get_description()
    start, end = get_times()

    return {
        "bucket": bucket,
        "description": description,
        "dates": [start, end]
    }