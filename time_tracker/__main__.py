import os, tomllib
from .time_tracker import TimeTracker
from .config import ConfigClass

if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__), "config.toml"), "rb") as f:
        configuration = ConfigClass(**tomllib.load(f))

    try:
        time_tacker = TimeTracker(configuration)
        while True:
            time_tacker.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
