import contextlib
import re, datetime
from .config import ConfigClass
from .notionapi import NotionAPI, Bucket


def run(configuration: ConfigClass):
    # Get current week times
    notionAPI = NotionAPI(configuration)

    curr_week_hours, last_week_hours = notionAPI.retrieve_hours()
    print(f"Current week hours -> {curr_week_hours}")

    diff = get_diff(configuration.weekly_hours, last_week_hours)
    if diff > 0:
        print(f"Hours from last week -> {diff}")
    print(f"Remaining hours -> {configuration.weekly_hours + diff - curr_week_hours}")

    # Get new time entry
    parsed_input = get_input_dict(notionAPI.buckets)

    # Confirm Input
    print("\nConfirm Data? (Y/N)")
    for key, value in parsed_input.items():
        print(f"  {key} -> {value}")
    response = input("> ")
    if response.strip().lower() == "n":
        return

    # Send POST request with new time entry
    db_page = notionAPI.build_db_page(parsed_input["description"], parsed_input["bucket"], parsed_input["dates"])
    notionAPI.send_time_entry(db_page)

    print("New time entry successfully added!")


def get_diff(weekly_hours: int, last_week_hours: float):
    return weekly_hours - last_week_hours if last_week_hours < weekly_hours else 0


def get_bucket(buckets: list[Bucket]) -> Bucket:
    while True:
        print("Available Buckets:")
        for i, b in enumerate(buckets):
            print(f"  {i} - {b.name}")

        with contextlib.suppress(IndexError):
            bucket = str(re.findall(r"\s*(\S+)\s*", input("Choose Bucket\n> "))[0])

            # Get bucket by index
            if bucket.isdigit():
                bucket = int(bucket)
                if bucket < len(buckets) and bucket >= 0:
                    return buckets[bucket]
                print(f"Illegal index {bucket} - Only {len(buckets)} available")
                continue

            if bucket in buckets:
                return buckets[buckets.index(bucket)]
            print("Illegal Bucket")


def get_description() -> str:
    while True:
        with contextlib.suppress(IndexError):
            return re.findall(r"\s*(\S+.*\S+)\s*", input("Insert Short Description\n> "))[0]


def build_time(raw_time):
    hours = int(raw_time[0])
    minutes = int(raw_time[1]) if raw_time[1] != "" else 0
    return datetime.time(hours, minutes)


def today_with_time(time: datetime.time) -> datetime.datetime:
    today = datetime.date.today()
    return datetime.datetime(today.year, today.month, today.day, time.hour, time.minute, time.second)


def get_times() -> tuple[str, str]:
    while True:
        with contextlib.suppress(IndexError):
            raw_input = input("Insert Start and End Times\n> ")
            raw_times = re.findall(r"\s*(\d{1,2})[:\.]?(\d{2})?\s*", raw_input)
            # raw_times.extend(re.findall(r"\s*(1\d{1})[:\.]?(\d{1,2})?\s*", raw_input))
            # raw_times.extend(re.findall(r"\s*(2[0-3])[:\.]?(\d{1,2})?\s*", raw_input))
            if len(raw_times) < 2:
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
                start_time, end_time = end_time, start_time
            break
    return (
        today_with_time(start_time).isoformat(),
        today_with_time(end_time).isoformat(),
    )


def get_input_dict(buckets: list[Bucket]) -> dict:
    bucket = get_bucket(buckets)
    description = get_description()
    start, end = get_times()

    return {"bucket": bucket, "description": description, "dates": [start, end]}
