import os
from datetime import datetime
from importlib import import_module
from logging import (
    ERROR,
    INFO,
    FileHandler,
    Formatter,
    LogRecord,
    StreamHandler,
    basicConfig,
    getLogger,
)
from logging import (
    error as log_error,
)
from logging import (
    info as log_info,
)
from os import path, remove
from subprocess import run as srun
from sys import exit

from pymongo.mongo_client import MongoClient
from pytz import timezone

getLogger("pymongo").setLevel(ERROR)

if path.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

if path.exists("rlog.txt"):
    remove("rlog.txt")


class CustomFormatter(Formatter):
    def formatTime(  # noqa: N802
        self,
        record: LogRecord,
        datefmt: str | None,
    ) -> str:
        dt: datetime = datetime.fromtimestamp(
            record.created,
            tz=timezone("Asia/Dhaka"),
        )
        return dt.strftime(datefmt)

    def format(self, record: LogRecord) -> str:
        return super().format(record).replace(record.levelname, record.levelname[:1])


formatter = CustomFormatter(
    "[%(asctime)s] %(levelname)s - %(message)s [%(module)s:%(lineno)d]",
    datefmt="%d-%b %I:%M:%S %p",
)

file_handler = FileHandler("log.txt")
file_handler.setFormatter(formatter)

stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)

basicConfig(handlers=[file_handler, stream_handler], level=INFO)

# Attempt to load from config.py
try:
    settings = import_module("config")
    config_file = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in vars(settings).items()
    }
except Exception:
    log_info(
        "The 'config.py' file is missing! Falling back to environment variables.",
    )
    config_file = {}

# Fallback to environment variables if BOT_TOKEN is not set
BOT_TOKEN = config_file.get("BOT_TOKEN") or os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    log_error("BOT_TOKEN variable is missing! Exiting now.")
    exit(1)

BOT_ID = BOT_TOKEN.split(":", 1)[0]

# Fallback to environment variables for DATABASE_URL
DATABASE_URL = config_file.get("DATABASE_URL", "") or os.getenv("DATABASE_URL", "")

if DATABASE_URL is not None:
    conn = MongoClient(DATABASE_URL)
    db = conn.tgh
    old_config = db.settings.deployConfig.find_one({"_id": bot_id})
    config_dict = db.settings.config.find_one({"_id": bot_id})
    if old_config is not None:
        del old_config["_id"]
    if (
        (old_config is not None and old_config == dict(dotenv_values("config.env")))
        or old_config is None
    ) and config_dict is not None:
        environ["UPSTREAM_REPO"] = config_dict["UPSTREAM_REPO"]
        environ["UPSTREAM_BRANCH"] = config_dict["UPSTREAM_BRANCH"]
        environ["UPGRADE_PACKAGES"] = config_dict.get("UPDATE_PACKAGES", "False")
    conn.close()

UPGRADE_PACKAGES = config_file.get("UPGRADE_PACKAGES", "False")
if UPGRADE_PACKAGES.lower() == "true":
    packages = [dist.project_name for dist in working_set]
    scall("uv pip install --system " + " ".join(packages), shell=True)

UPSTREAM_REPO = config_file.get("UPSTREAM_REPO", "")
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None

UPSTREAM_BRANCH = config_file.get("UPSTREAM_BRANCH", "")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "HuntingBots"

if UPSTREAM_REPO is not None:
    if ospath.exists(".git"):
        srun(["rm", "-rf", ".git"], check=False)

    update = srun(
        [
            f"git init -q \
                     && git config --global user.email doc.adhikari@gmail.com \
                     && git config --global user.name weebzone \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"
        ],
        shell=True,
        check=False,
    )

    repo = UPSTREAM_REPO.split("/")
    UPSTREAM_REPO = f"https://github.com/{repo[-2]}/{repo[-1]}"
    if update.returncode == 0:
        log_info("Successfully updated with latest commits !!")
    else:
        log_error("Something went Wrong ! Retry or Ask Support !")
    log_info(f"UPSTREAM_REPO: {UPSTREAM_REPO} | UPSTREAM_BRANCH: {UPSTREAM_BRANCH}")

urun(
    [
        "rm",
        "-rf",
        "py_generators",
        "config_sample.env",
        "Dockerfile",
        "LICENSE",
        "README.md",
        "requirements.txt",
    ],
)
