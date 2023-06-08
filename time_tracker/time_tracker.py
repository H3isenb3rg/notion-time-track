import re, datetime

from .config import ConfigClass, CFG_LOC
from .notionapi import NotionAPI, Bucket
from .timeentry import build_db_page
from .richprinter import print_options_as_tree, print_title, print_markdown


class TimeTracker:
    AVAILABLE_ACTIONS: tuple = ("time", "recap", "settings")

    def __init__(self, configuration: ConfigClass) -> None:
        self.configs = configuration
        self.notionAPI = NotionAPI(self.configs)

    def launch(self):
        print_title("Welcome to the Notion time tracker API!")
        curr_week_hours, last_week_hours = self.notionAPI.retrieve_hours()
        print_markdown(f"Current week hours &rarr; {curr_week_hours}")
        self.print_diff(last_week_hours, curr_week_hours)

        action = self._get_main_action()
        if action == "time":
            self.run_time_tracker()
            input("\nPress Enter to continue")
            return

        if action == "settings":
            self.run_settings()
            input("\nPress Enter to continue")
            return

        if action == "recap":
            recap_dict = self.notionAPI.build_recap()
            for key in recap_dict:
                print_options_as_tree(key, recap_dict[key], add_index=False)
            input("\nPress Enter to continue")
            return

    def run_time_tracker(self):
        # Get new time entry
        parsed_input = self.get_new_entry()

        # Confirm Input
        if self._get_input_confirmation(parsed_input) not in ["y", "yes"]:
            self.run_time_tracker()

        # Send POST request with new time entry
        db_page = build_db_page(
            parsed_input["description"],
            parsed_input["bucket"],
            parsed_input["dates"],
            self.configs.time_entries_db_id,
        )
        self.notionAPI.send_time_entry(db_page)

        print_markdown("New time entry successfully added!", style="green bold")

    def run_settings(self):
        print_options_as_tree(
            "Current Settings",
            [
                f"Weekly Sentric Hours: {self.configs.weekly_hours}",
                f"Bucket Area: {self.configs.bucket_area}",
            ],
            add_index=False,
        )
        # clickable link -> not working in cmd
        # cfg_loc_link = f"\u001b]8;;{CFG_LOC}\u001b\\{CFG_LOC}\u001b]8;;\u001b\\"
        print_markdown(f"Settings available at: {CFG_LOC}")

    def print_diff(self, last_week_hours: float, curr_week_hours: float):
        diff = self.configs.weekly_hours - last_week_hours
        if diff > 0:
            print_markdown(f"Hours pending from last week &rarr; {diff}", style="yellow")

        if diff < 0:
            print_markdown(f"Hours overflowed from last week &rarr; {abs(diff)}", style="green")

        remaining_hours = self.configs.weekly_hours + diff - curr_week_hours
        print_markdown(
            f"Remaining hours &rarr; {remaining_hours}",
            style="yellow" if remaining_hours < self.configs.weekly_hours else "green",
        )

    def get_bucket(self) -> Bucket:
        while True:
            bucket = self._get_input_bucket()

            try:
                return self.notionAPI.buckets[int(bucket)]
            except IndexError:
                print_markdown(
                    f"Illegal index {bucket} - Only {len(self.notionAPI.buckets)} available",
                    style="red",
                )
            except ValueError:
                try:
                    return self.notionAPI.buckets[self.notionAPI.buckets.index(bucket)]  # type: ignore
                except ValueError:
                    print_markdown("Illegal Bucket", style="red")

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
                print_markdown("Missing time stamp", style="red")
                continue

            try:
                start_time = self.build_time(raw_times[0])
                end_time = self.build_time(raw_times[1])
            except ValueError:
                print_markdown("Wrong Time values. Insert valid 24h times", style="red")
                continue

            if start_time == end_time:
                print_markdown(f"Same time for start and end found: {start_time}", style="red")
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
        print_options_as_tree("Available Buckets", self.notionAPI.buckets)
        return input("Choose Bucket\n> ").strip()

    def _get_input_confirmation(self, parsed_input: dict):
        print_options_as_tree(
            "Confirm Data?",
            [f"{key} &rarr; {value}" for key, value in parsed_input.items()],
            add_index=False,
        )
        return input("(y/n)> ").strip().lower()

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
            print_markdown("Invalid input!")
