import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / "env.json"


def load_env():
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            return json.load(f)
    return {}


env = load_env()


class Config:

    ENV = os.environ.get("ENV", env.get("ENV", "local")).lower()

    if ENV == "cloud":
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            env.get("CLOUD_DB_URL")
        )

    elif ENV == "docker":
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            env.get("DOCKER_DB_URL")
        )

    else:  # local default
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            env.get("LOCAL_DB_URL")
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", env.get("SECRET_KEY", "supersecretkey"))
