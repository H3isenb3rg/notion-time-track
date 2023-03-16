import re, datetime

from .config import ConfigClass, CFG_LOC
from .notionapi import NotionAPI, Bucket
from .timeentry import build_db_page
from .richprinter import print_options_as_tree, print_title


class TimeTracker:
    AVAILABLE_ACTIONS: tuple = ("time", "recap", "settings")

    def __init__(self, configuration: ConfigClass) -> None:
        self.configs = configuration
        self.notionAPI = NotionAPI(self.configs)

    def launch(self):
        print_title("Welcome to the Notion time tracker API!")

        action = self._get_main_action()
        if action == "time":
            self.run_time_tracker()
            return

        if action == "settings":
            self.run_settings()
            return

        if action == "recap":
            print(self.notionAPI.build_recap())
            return

    def run_time_tracker(self):
        curr_week_hours, last_week_hours = self.notionAPI.retrieve_hours()
        print(f"Current week hours -> {curr_week_hours}")
        self.print_diff(last_week_hours, curr_week_hours)

        # Get new time entry
        parsed_input = self.get_new_entry()

        # Confirm Input
        if self._get_input_confirmation(parsed_input) not in ["y", "yes"]:
            self.run_time_tracker()

        # Send POST request with new time entry
        db_page = build_db_page(parsed_input["description"], parsed_input["bucket"], parsed_input["dates"], self.configs.time_entries_db_id)
        self.notionAPI.send_time_entry(db_page)

        print("New time entry successfully added!")

    def run_settings(self):
        print("Current Settings:")
        print(f"1. Weekly Sentric Hours: {self.configs.weekly_hours}")
        print(f"2. Bucket Area: {self.configs.bucket_area}")
        print(f"Settings available at: {CFG_LOC}")

    def print_diff(self, last_week_hours: float, curr_week_hours: float):
        diff = self.configs.weekly_hours - last_week_hours
        if diff > 0:
            print(f"Hours pending from last week -> {diff}")

        if diff < 0:
            print(f"Hours overflowed from last week -> {abs(diff)}")

        print(f"Remaining hours -> {self.configs.weekly_hours + diff - curr_week_hours}")

    def get_bucket(self) -> Bucket:
        while True:
            bucket = self._get_input_bucket()

            try:
                return self.notionAPI.buckets[int(bucket)]
            except IndexError:
                print(f"Illegal index {bucket} - Only {len(self.notionAPI.buckets)} available")
            except ValueError:
                try:
                    return self.notionAPI.buckets[self.notionAPI.buckets.index(bucket)]  # type: ignore
                except ValueError:
                    print("Illegal Bucket")

    def get_description(self) -> str:
        while True:
            description = input("Insert Short Description\n> ").strip()
            if description != "":
                return description

    def build_time(self, raw_time):
        hours = int(raw_time[0])
        minutes = int(raw_time[1]) if raw_time[1] != "" else 0
        return datetime.time(hours, minutes)

    def today_with_time(self, time: datetime.time) -> str:
        today = datetime.date.today()
        return datetime.datetime(today.year, today.month, today.day, time.hour, time.minute, time.second).isoformat()

    def get_times(self) -> tuple[str, str]:
        while True:
            try:
                raw_times = self._get_raw_times()
            except ValueError:
                print("Missing time stamp")
                continue

            try:
                start_time = self.build_time(raw_times[0])
                end_time = self.build_time(raw_times[1])
            except ValueError:
                print("Wrong Time values. Insert valid 24h times")
                continue

            if start_time == end_time:
                print(f"Same time for start and end found: {start_time}")
                continue

            if start_time > end_time:
                start_time, end_time = end_time, start_time

            return (self.today_with_time(start_time), self.today_with_time(end_time))

    def _get_raw_times(self):
        raw_input = input("Insert Start and End Times\n> ")
        raw_times = re.findall(r"\s*(\d{1,2})[:\.]?(\d{2})?\s*", raw_input)
        if len(raw_times) < 2:
            raise ValueError

        return raw_times

    def get_new_entry(self) -> dict:
        bucket = self.get_bucket()
        description = self.get_description()
        start, end = self.get_times()

        return {"bucket": bucket, "description": description, "dates": [start, end]}

    def _get_input_bucket(self) -> str:
        prompt = "Available Buckets:\n" + "\n".join(f"  {i} - [{b.area}] {b.name}" for i, b in enumerate(self.notionAPI.buckets)) + "\nChoose Bucket\n> "
        return input(prompt).strip()

    def _get_input_confirmation(self, parsed_input: dict):
        prompt = "\nConfirm Data? (Y/N)\n" + "\n".join(f"  {key} -> {value}" for key, value in parsed_input.items()) + "\n> "
        return input(prompt).strip().lower()

    def _get_main_action(self):
        print_options_as_tree("What would you like to do?", self.AVAILABLE_ACTIONS)
        while True:
            action = input("> ").strip().lower()
            try:
                action = int(action)
                if action >= 0 and action < len(self.AVAILABLE_ACTIONS):
                    return self.AVAILABLE_ACTIONS[action]
            except ValueError:
                if action in self.AVAILABLE_ACTIONS:
                    return action
            print("Invalid input!")
