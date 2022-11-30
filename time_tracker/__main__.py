import os, tomllib
from . import app
from .config import ConfigClass

if __name__=="__main__":
    with open(os.path.join(os.path.dirname(__file__), "config.toml"), "rb") as f:
        configuration = ConfigClass(**tomllib.load(f))

    try:
        app.run(configuration)
    except KeyboardInterrupt as e:
        print("\nGoodbye!")