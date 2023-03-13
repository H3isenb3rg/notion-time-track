from .time_tracker import TimeTracker
from .config import load_config

import requests

try:
    tt = TimeTracker(load_config())
    while True:
        tt.launch()
except requests.exceptions.HTTPError as e:
    print(f"Received HTTPError:\n\t{e}")
except KeyboardInterrupt:
    print("\nGoodbye!")
