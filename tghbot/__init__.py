# ruff: noqa: E402
from uvloop import install

install()

import os
import subprocess
from asyncio import Lock, new_event_loop, set_event_loop
from datetime import datetime
from logging import (
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    Formatter,
    LogRecord,
    StreamHandler,
    basicConfig,
    getLogger,
)
from time import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from uvloop import install

from sabnzbdapi import SabnzbdClient

getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("pyrogram").setLevel(ERROR)
getLogger("httpx").setLevel(WARNING)
getLogger("pymongo").setLevel(WARNING)
getLogger("aiohttp").setLevel(WARNING)

bot_start_time = time()

bot_loop = new_event_loop()
set_event_loop(bot_loop)


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

LOGGER = getLogger(__name__)

cpu_no = os.cpu_count()

DOWNLOAD_DIR = "/usr/src/app/downloads/"
intervals = {
    "status": {},
    "qb": "",
    "jd": "",
    "nzb": "",
    "stopAll": False,
}
qb_torrents = {}
user_data = {}
aria2_options = {}
qbit_options = {}
nzb_options = {}
queued_dl = {}
queued_up = {}
status_dict = {}
task_dict = {}
jd_downloads = {}
nzb_jobs = {}
rss_dict = {}
auth_chats = {}
excluded_extensions = ["aria2", "!qB"]
drives_names = []
drives_ids = []
index_urls = []
sudo_users = []
non_queued_dl = set()
non_queued_up = set()
multi_tags = set()
task_dict_lock = Lock()
queue_dict_lock = Lock()
qb_listener_lock = Lock()
cpu_eater_lock = Lock()
same_directory_lock = Lock()
nzb_listener_lock = Lock()
jd_listener_lock = Lock()
shorteners_list = []

sabnzbd_client = SabnzbdClient(
    host="http://localhost",
    api_key="mltb",
    port="8070",
)
subprocess.run(["xnox", "-d", f"--profile={os.getcwd()}"], check=False)
subprocess.run(
    [
        "xnzb",
        "-f",
        "sabnzbd/SABnzbd.ini",
        "-s",
        ":::8070",
        "-b",
        "0",
        "-d",
        "-c",
        "-l",
        "0",
        "--console",
    ],
    check=False,
)


scheduler = AsyncIOScheduler(event_loop=bot_loop)


BOT_TOKEN = environ.get(
    "BOT_TOKEN",
    ""
)
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

BOT_ID = BOT_TOKEN.split(
    ":",
    1
)[0]

DATABASE_URL = environ.get(
    "DATABASE_URL",
    ""
)
if len(DATABASE_URL) == 0:
    DATABASE_URL = ""

if DATABASE_URL:
    try:
        conn = MongoClient(
            DATABASE_URL,
            server_api=ServerApi("1")
        )
        db = conn.tgh
        current_config = dict(dotenv_values("config.env"))
        old_config = db.settings.deployConfig.find_one({"_id": BOT_ID})
        if old_config is None:
            db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_config,
                upsert=True
            )
        else:
            del old_config["_id"]
        if (
            old_config
            and old_config != current_config
        ):
            db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_config,
                upsert=True
            )
        elif config_dict := db.settings.config.find_one({"_id": BOT_ID}):
            del config_dict["_id"]
            for key, value in config_dict.items():
                environ[key] = str(value)
        if pf_dict := db.settings.files.find_one({"_id": BOT_ID}):
            del pf_dict["_id"]
            for key, value in pf_dict.items():
                if value:
                    file_ = key.replace(
                        "__",
                        "."
                    )
                    with open(
                        file_,
                        "wb+"
                    ) as f:
                        f.write(value)
        if a2c_options := db.settings.aria2c.find_one({"_id": BOT_ID}):
            del a2c_options["_id"]
            aria2_options = a2c_options
        if qbit_opt := db.settings.qbittorrent.find_one({"_id": BOT_ID}):
            del qbit_opt["_id"]
            qbit_options = qbit_opt
        if nzb_opt := db.settings.nzb.find_one({"_id": BOT_ID}):
            if ospath.exists("sabnzbd/SABnzbd.ini.bak"):
                remove("sabnzbd/SABnzbd.ini.bak")
            del nzb_opt["_id"]
            ((key, value),) = nzb_opt.items()
            file_ = key.replace("__", ".")
            with open(f"sabnzbd/{file_}", "wb+") as f:
                f.write(value)
        conn.close()
        BOT_TOKEN = environ.get(
            "BOT_TOKEN",
            ""
        )
        BOT_ID = BOT_TOKEN.split(
            ":",
            1
        )[0]
        DATABASE_URL = environ.get(
            "DATABASE_URL",
            ""
)

