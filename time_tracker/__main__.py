from .time_tracker import TimeTracker
from .config import load_config

import requests

try:
    TimeTracker(load_config()).run_time_tracker()
except requests.exceptions.HTTPError as e:
    print(f"Received HTTPError:\n\t{e}")
except KeyboardInterrupt:
    print("\nGoodbye!")
