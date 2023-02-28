from .time_tracker import TimeTracker
from .config import load_config


TimeTracker(load_config()).run()
