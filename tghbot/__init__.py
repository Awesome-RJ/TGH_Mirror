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
    "
