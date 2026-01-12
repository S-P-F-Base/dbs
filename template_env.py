import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOCAL_RUN = os.getenv("FASTAPISTATIC") == "1"
SVC_ID = "users_api"
