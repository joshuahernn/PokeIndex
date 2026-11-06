import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Docker supplies connection settings; local runs use the backend .env file.
if "PGHOST" not in os.environ:
    load_dotenv(Path(__file__).with_name(".env"))


def get_connection():
    return psycopg.connect()
