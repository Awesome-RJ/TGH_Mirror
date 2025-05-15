import asyncio
from asyncio import create_subprocess_exec, create_subprocess_shell
from os import environ

import httpx
from aiofiles import open as aiopen
from aiofiles.os import makedirs, remove
from aiofiles.os import path as aiopath
from aioshutil import rmtree

from sabnzbdapi import SabnzbdClient
from tghbot import (
    LOGGER,
    aria2_options,
    auth_chats,
    drives_ids,
    drives_names,
    excluded_extensions,
    index_urls,
    nzb_options,
    qbit_options,
    rss_dict,
    shorteners_list,
    sudo_users,
    user_data,
)
from tghbot.core.config_manager import Config
from tghbot.core.tgh_client import TgClient
from tghbot.core.torrent_manager import TorrentManager
from tghbot.helper.ext_utils.db_handler import database


async def update_qb_options():
    if not qbit_options:
        opt = await TorrentManager.qbittorrent.app.preferences()
        qbit_options.update(opt)
        del qbit_options["listen_port"]
        for k in list(qbit_options.keys()):
            if k.startswith("rss"):
                del qbit_options[k]
        qbit_options["web_ui_password"] = "mltbmltb"
        await TorrentManager.qbittorrent.app.set_preferences(
            {"web_ui_password": "mltbmltb"},
        )
    else:
        await TorrentManager.qbittorrent.app.set_preferences(qbit_options)


async def update_aria2_options():
    if not aria2_options:
        op = await TorrentManager.aria2.getGlobalOption()
        aria2_options.update(op)
    else:
        await TorrentManager.aria2.changeGlobalOption(aria2_options)


async def update_nzb_options():
    sabnzbd_client_instance = SabnzbdClient(
        host="http://localhost",  # Update this to the correct host
        api_key="mltb",          # Ensure this API key is correct
        port="8070",             # Verify the port
    )
    retries = 3
    for attempt in range(retries):
        try:
            LOGGER.info(f"Attempting to connect to Sabnzbd (Attempt {attempt + 1}/{retries})...")
            no = (await sabnzbd_client_instance.get_config())["config"]["misc"]
            nzb_options.update(no)
            LOGGER.info(
                f"Successfully connected to Sabnzbd on attempt {attempt + 1}",
            )
            break
        except (httpx.ConnectError, httpx.RequestError) as e:
            LOGGER.error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                LOGGER.info("Retrying connection after delay...")
                await asyncio.sleep(2**attempt)
            else:
                LOGGER.error("All connection attempts to Sabnzbd failed. Please check the service status and configuration.")
                raise e


async def load_settings():
    if not Config.DATABASE_URL:
        return
    for p in ["thumbnails", "tokens", "rclone"]:
        if await aiopath.exists(p):
            await rmtree(p, ignore_errors=True)
    await database.connect()
    if database.db is not None:
        BOT_ID = Config.BOT_TOKEN.split(":", 1)[0]
        current_deploy_config = Config.get_all()
        old_deploy_config = await database.db.settings.deployConfig.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        )

        if old_deploy_config is None:
            await database.db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_deploy_config,
            )


# Add the missing load_configurations function
async def load_configurations():
    """
    This function is a placeholder to resolve the ImportError.
    Replace it with the actual logic needed for loading configurations.
    """
    LOGGER.info("Loading configurations...")
    # Implement the logic for loading configurations here
    await load_settings()
    LOGGER.info("Configurations loaded successfully.")
