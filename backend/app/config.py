import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(
        dotenv_path=ENV_FILE,
        override=False,
    )


DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)