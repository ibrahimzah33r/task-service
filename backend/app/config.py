import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

if not ENV_FILE.exists():
    raise RuntimeError(
        f".env file not found at {ENV_FILE}"
    )

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)

DATABASE_URL = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]