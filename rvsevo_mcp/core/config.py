
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

RVSEVO_BASE_URL = os.getenv("RVSEVO_BASE_URL")
RVSEVO_USERNAME = os.getenv("RVSEVO_USERNAME")
RVSEVO_PASSWORD = os.getenv("RVSEVO_PASSWORD")


def require_rvs_evo_config() -> None:
    """Validate that the required rvsEVO credentials are configured."""
    if not RVSEVO_BASE_URL:
        raise RuntimeError("RVSEVO_BASE_URL is not configured.")

    if not RVSEVO_USERNAME:
        raise RuntimeError("RVSEVO_USERNAME is not configured.")

    if not RVSEVO_PASSWORD:
        raise RuntimeError("RVSEVO_PASSWORD is not configured.")


