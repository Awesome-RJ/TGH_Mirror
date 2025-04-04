# ruff: noqa: E402
from socket import setdefaulttimeout

from uvloop import install

install()
setdefaulttimeout(600)

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
from os import environ, getcwd
from os import path as ospath
from os import remove as osremove
from subprocess import Popen
from subprocess import run as srun
from time import sleep, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aria2p import API as ariaAPI
from aria2p import Client as ariaClient
from pytz import timezone
from qbittorrentapi import Client as qbClient

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

if ospath.exists("shorteners.txt"):
    with open("shorteners.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            if len(temp) == 2:
                shorteners_list.append({"domain": temp[0], "api_key": temp[1]})

if "BASE_URL" in locals():
    Popen(
        f"gunicorn web.wserver:app --bind 0.0.0.0:{BASE_URL_PORT} --worker-class gevent",
        shell=True,
    )

srun(["qbittorrent-nox", "-d", f"--profile={getcwd()}"], check=False)
if not ospath.exists(".netrc"):
    with open(".netrc", "w"):
        pass
srun(["chmod", "600", ".netrc"], check=False)
srun(["cp", ".netrc", "/root/.netrc"], check=False)
srun(["chmod", "+x", "aria.sh"], check=False)
srun("./aria.sh", shell=True, check=False)
if ospath.exists("accounts.zip"):
    if ospath.exists("accounts"):
        srun(["rm", "-rf", "accounts"], check=False)
    srun(["7z", "x", "-o.", "-aoa", "accounts.zip", "accounts/*.json"], check=False)
    srun(["chmod", "-R", "777", "accounts"], check=False)
    osremove("accounts.zip")
if not ospath.exists("accounts"):
    config_dict["USE_SERVICE_ACCOUNTS"] = False
sleep(0.5)

aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))


def get_client():
    return qbClient(
        host="localhost",
        port=8090,
        VERIFY_WEBUI_CERTIFICATE=False,
        REQUESTS_ARGS={"timeout": (30, 60)},
    )


def aria2c_init():
    try:
        LOGGER.info("Initializing Aria2c")
        link = "https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent"
        dire = DOWNLOAD_DIR.rstrip("/")
        aria2.add_uris([link], {"dir": dire})
        sleep(3)
        downloads = aria2.get_downloads()
        sleep(10)
        aria2.remove(downloads, force=True, files=True, clean=True)
    except Exception as e:
        LOGGER.error(f"Aria2c initializing error: {e}")


Thread(target=aria2c_init).start()
sleep(1.5)

aria2c_global = [
    "bt-max-open-files",
    "download-result",
    "keep-unfinished-download-result",
    "log",
    "log-level",
    "max-concurrent-downloads",
    "max-download-result",
    "max-overall-download-limit",
    "save-session",
    "max-overall-upload-limit",
    "optimize-concurrent-downloads",
    "save-cookies",
    "server-stat-of",
]

if not aria2_options:
    aria2_options = aria2.client.get_global_option()
else:
    a2c_glo = {op: aria2_options[op] for op in aria2c_global if op in aria2_options}
    aria2.set_global_options(a2c_glo)

qb_client = get_client()
if not qbit_options:
    qbit_options = dict(qb_client.app_preferences())
    del qbit_options["listen_port"]
    for k in list(qbit_options.keys()):
        if k.startswith("rss"):
            del qbit_options[k]
else:
    qb_opt = {**qbit_options}
    for k, v in list(qb_opt.items()):
        if v in ["", "*"]:
            del qb_opt[k]
    qb_client.app_set_preferences(qb_opt)


scheduler = AsyncIOScheduler(event_loop=bot_loop)
