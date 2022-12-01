import requests, json, re, datetime
from .config import ConfigClass
from .notionapi import NotionAPI
    

def run(configuration: ConfigClass):
    # Get current week times
    notionAPI = NotionAPI(configuration)

    curr_week_hours, last_week_hours = notionAPI.retrieve_hours()
    print(f"Current week hours -> {curr_week_hours}")
    
    diff = configuration.weekly_hours - last_week_hours if last_week_hours<configuration.weekly_hours else 0
    if diff>0: print(f'Hours from last week -> {diff}')
    print(f"Remaining hours -> {configuration.weekly_hours + diff - curr_week_hours}")

    # Get new time entry
    parsed_input = get_input_dict(configuration.allowed_buckets)

    # Confirm Input
    print(json.dumps(parsed_input, indent=2))
    response = input("Confirm Data? (Y/N)\n> ")
    if response.strip().lower() == "n":
        return

    # Send POST request with new time entry
    db_page = notionAPI.build_db_page(parsed_input["description"], parsed_input["bucket"], parsed_input["dates"])
    notionAPI.send_time_entry(db_page)

    print("New time entry successfully added!")

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
        except IndexError:
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

def get_input_dict(allowed_buckets: dict[str, str]) -> dict:
    bucket = get_bucket(allowed_buckets).lower()
    description = get_description()
    start, end = get_times()

    return {
        "bucket": bucket,
        "description": description,
        "dates": [start, end]
    }