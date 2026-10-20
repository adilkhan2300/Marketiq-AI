import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = f"sqlite:///{BASE_DIR}/marketiq.db"

DEFAULT_CURRENCY = "USD"
DEFAULT_CURRENCY_SYMBOL = "$"
PROJECT_NAME = "MARKETIQ AI"
TAGLINE = "Turn Marketing Spend into Measurable Growth"
VERSION = "1.0.0"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DATA_DIR / "uploads", exist_ok=True)
os.makedirs(DATA_DIR / "demo", exist_ok=True)
os.makedirs(DATA_DIR / "exports", exist_ok=True)
