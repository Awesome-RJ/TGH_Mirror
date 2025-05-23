# ruff: noqa: E402
import os
import subprocess
import time
from asyncio import Lock, new_event_loop, set_event_loop
from datetime import datetime
from importlib import import_module
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
from os import environ, getcwd, remove as osremove, path as ospath
from subprocess import Popen, run as srun
from threading import Thread

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aria2p import API as ariaAPI
from aria2p import Client as ariaClient
from pytz import timezone
from qbittorrentapi import Client as qbClient
from socket import setdefaulttimeout
from uvloop import install

# Initialize uvloop and set default socket timeout
install()
setdefaulttimeout(600)

# Suppress warnings from external libraries
getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("pyrogram").setLevel(ERROR)
getLogger("httpx").setLevel(WARNING)
getLogger("pymongo").setLevel(WARNING)
getLogger("aiohttp").setLevel(WARNING)

# Bot start time
bot_start_time = time.time()

# Set up asyncio event loop for the bot
bot_loop = new_event_loop()
set_event_loop(bot_loop)

# --- Logging Configuration ---
class CustomFormatter(Formatter):
    """Custom log formatter to include Asia/Dhaka timezone and single-letter level."""

    def formatTime(self, record: LogRecord, datefmt: str | None) -> str:
        """Format the log record time with Asia/Dhaka timezone."""
        dt: datetime = datetime.fromtimestamp(
            record.created,
            tz=timezone("Asia/Dhaka"),
        )
        return dt.strftime(datefmt)

    def format(self, record: LogRecord) -> str:
        """Format the log record, replacing level name with its first letter."""
        return super().format(record).replace(record.levelname, record.levelname[:1])

# Create formatter, file handler, and stream handler
formatter = CustomFormatter(
    "[%(asctime)s] %(levelname)s - %(message)s [%(module)s:%(lineno)d]",
    datefmt="%d-%b %I:%M:%S %p",
)
file_handler = FileHandler("log.txt")
file_handler.setFormatter(formatter)
stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)

# Configure basic logging
basicConfig(handlers=[file_handler, stream_handler], level=INFO)
LOGGER = getLogger(__name__)

# --- Global Variables ---
cpu_no = os.cpu_count()
DOWNLOAD_DIR = "/usr/src/app/downloads/"

# Dictionaries and sets for managing bot state
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
shorteners_list = []

# Locks for thread-safe operations
task_dict_lock = Lock()
queue_dict_lock = Lock()
qb_listener_lock = Lock()
cpu_eater_lock = Lock()
same_directory_lock = Lock()
nzb_listener_lock = Lock()
jd_listener_lock = Lock()


# --- Configuration Loading ---
config_file = {}
try:
    settings = import_module("config")
    config_file = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in vars(settings).items()
    }
except ImportError:
    LOGGER.warning("The 'config.py' file is missing! Falling back to environment variables.")
except Exception as e:
    LOGGER.error(f"Error loading config.py: {e}")

# Load shorteners list from file
if ospath.exists("shorteners.txt"):
    with open("shorteners.txt", "r+") as f:
        for line in f:
            temp = line.strip().split()
            if len(temp) == 2:
                shorteners_list.append({"domain": temp[0], "api_key": temp[1]})

# --- Initial Setup and Service Initialization ---

# Start web server if BASE_URL is defined
if "BASE_URL" in locals():
    # Use config_file for BASE_URL_PORT if available, otherwise assume default
    port = config_file.get("BASE_URL_PORT", 80) # Default to 80 if not specified
    Popen(
        f"gunicorn web.wserver:app --bind 0.0.0.0:{port} --worker-class gevent",
        shell=True,
    )

# Start qBittorrent-nox
LOGGER.info("Starting qBittorrent-nox...")
srun(["qbittorrent-nox", "-d", f"--profile={getcwd()}"], check=False)

# Configure .netrc
if not ospath.exists(".netrc"):
    with open(".netrc", "w"):
        pass
srun(["chmod", "600", ".netrc"], check=False)
srun(["cp", ".netrc", "/root/.netrc"], check=False)

# Set up Aria2
LOGGER.info("Setting up Aria2...")
srun(["chmod", "+x", "aria.sh"], check=False)
srun("./aria.sh", shell=True, check=False)

# Handle service accounts
if ospath.exists("accounts.zip"):
    if ospath.exists("accounts"):
        srun(["rm", "-rf", "accounts"], check=False)
    srun(["7z", "x", "-o.", "-aoa", "accounts.zip", "accounts/*.json"], check=False)
    srun(["chmod", "-R", "777", "accounts"], check=False)
    osremove("accounts.zip")
if not ospath.exists("accounts"):
    config_file["USE_SERVICE_ACCOUNTS"] = False
time.sleep(0.5)

# Initialize Aria2 API
aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))

def get_qb_client() -> qbClient:
    """Returns a qBittorrent client instance."""
    return qbClient(
        host="localhost",
        port=8090,
        VERIFY_WEBUI_CERTIFICATE=False,
        REQUESTS_ARGS={"timeout": (30, 60)},
    )

def aria2c_init_check():
    """Initializes Aria2c by adding and removing a test download."""
    try:
        LOGGER.info("Initializing Aria2c by adding a test download...")
        link = "https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent"
        dire = DOWNLOAD_DIR.rstrip("/")
        test_download = aria2.add_uris([link], {"dir": dire})
        time.sleep(3)
        # Attempt to get downloads, then remove the test download
        downloads = aria2.get_downloads()
        if test_download in downloads:
            aria2.remove([test_download], force=True, files=True, clean=True)
        LOGGER.info("Aria2c initialization successful.")
    except Exception as e:
        LOGGER.error(f"Aria2c initializing error: {e}. Please check if Aria2c is running.")

# Run Aria2c initialization in a separate thread
Thread(target=aria2c_init_check).start()
time.sleep(1.5)

# Aria2c global options to manage
aria2c_global_options_to_manage = [
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

# Set Aria2 global options
if not aria2_options:
    aria2_options = aria2.client.get_global_option()
else:
    # Filter and set global options from config_file
    filtered_options = {
        op: aria2_options[op] for op in aria2c_global_options_to_manage if op in aria2_options
    }
    aria2.set_global_options(filtered_options)

# Initialize qBittorrent client and set preferences
qb_client = get_qb_client()
if not qbit_options:
    qbit_options = dict(qb_client.app_preferences())
    # Remove RSS related options and listen_port as they might be managed elsewhere or are dynamic
    qbit_options.pop("listen_port", None)
    for k in list(qbit_options.keys()):
        if k.startswith("rss"):
            del qbit_options[k]
else:
    # Apply qBittorrent options from config_file, filtering out empty/wildcard values
    qb_opt_to_set = {k: v for k, v in qbit_options.items() if v not in ["", "*"]}
    qb_client.app_set_preferences(qb_opt_to_set)

# Initialize APScheduler
scheduler = AsyncIOScheduler(event_loop=bot_loop)
