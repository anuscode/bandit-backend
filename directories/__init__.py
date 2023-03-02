import os

from pathlib import Path

project = Path(os.path.dirname(__file__)).parent

credentials = project.joinpath("credentials")

logging = project.joinpath("logging.yaml")
