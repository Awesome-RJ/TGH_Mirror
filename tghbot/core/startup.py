import asyncio

import httpx
from aiofiles import open as aiopen
from aiofiles.os import makedirs, remove
from aiofiles.os import path as aiopath
from aioshutil import rmtree

from sabnzbdapi import SabnzbdClient
from tghbot import (
    LOGGER,
    aria2_options,
    nzb_options,
    qbit_options,
    rss_dict,
    user_data,
)
from tghbot.core.config_manager import Config
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
        api_key="mltb",  # Ensure this API key is correct
        port="8070",  # Verify the port
    )
    retries = 3
    for attempt in range(retries):
        try:
            LOGGER.info(
                f"Attempting to connect to Sabnzbd (Attempt {attempt + 1}/{retries})...",
            )
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
                LOGGER.error(
                    "All connection attempts to Sabnzbd failed. Please check the service status and configuration.",
                )
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
                upsert=True,
            )
        elif old_deploy_config != current_deploy_config:
            runtime_config = (
                await database.db.settings.config.find_one(
                    {"_id": BOT_ID},
                    {"_id": 0},
                )
                or {}
            )

            new_vars = {
                k: v
                for k, v in current_deploy_config.items()
                if k not in runtime_config
            }
            if new_vars:
                runtime_config.update(new_vars)
                await database.db.settings.config.replace_one(
                    {"_id": BOT_ID},
                    runtime_config,
                    upsert=True,
                )
                LOGGER.info(f"Added new variables: {list(new_vars.keys())}")

            await database.db.settings.deployConfig.replace_one(
                {"_id": BOT_ID},
                current_deploy_config,
                upsert=True,
            )

        runtime_config = await database.db.settings.config.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        )
        if runtime_config:
            Config.load_dict(runtime_config)

        if pf_dict := await database.db.settings.files.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        ):
            for key, value in pf_dict.items():
                if value:
                    file_ = key.replace("__", ".")
                    async with aiopen(file_, "wb+") as f:
                        await f.write(value)

        if a2c_options := await database.db.settings.aria2c.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        ):
            aria2_options.update(a2c_options)

        if qbit_opt := await database.db.settings.qbittorrent.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        ):
            qbit_options.update(qbit_opt)

        if nzb_opt := await database.db.settings.nzb.find_one(
            {"_id": BOT_ID},
            {"_id": 0},
        ):
            if await aiopath.exists("sabnzbd/SABnzbd.ini.bak"):
                await remove("sabnzbd/SABnzbd.ini.bak")
            ((key, value),) = nzb_opt.items()
            file_ = key.replace("__", ".")
            async with aiopen(f"sabnzbd/{file_}", "wb+") as f:
                await f.write(value)

        if await database.db.users.find_one():
            for p in ["thumbnails", "tokens", "rclone"]:
                if not await aiopath.exists(p):
                    await makedirs(p)
            rows = database.db.users.find({})
            async for row in rows:
                uid = row["_id"]
                del row["_id"]
                thumb_path = f"thumbnails/{uid}.jpg"
                rclone_config_path = f"rclone/{uid}.conf"
                token_path = f"tokens/{uid}.pickle"
                if row.get("THUMBNAIL"):
                    async with aiopen(thumb_path, "wb+") as f:
                        await f.write(row["THUMBNAIL"])
                    row["THUMBNAIL"] = thumb_path
                if row.get("RCLONE_CONFIG"):
                    async with aiopen(rclone_config_path, "wb+") as f:
                        await f.write(row["RCLONE_CONFIG"])
                    row["RCLONE_CONFIG"] = rclone_config_path
                if row.get("TOKEN_PICKLE"):
                    async with aiopen(token_path, "wb+") as f:
                        await f.write(row["TOKEN_PICKLE"])
                    row["TOKEN_PICKLE"] = token_path
                user_data[uid] = row
            LOGGER.info("Users data has been imported from Database")

        if await database.db.rss[BOT_ID].find_one():
            rows = database.db.rss[BOT_ID].find({})
            async for row in rows:
                user_id = row["_id"]
                del row["_id"]
                rss_dict[user_id] = row
            LOGGER.info("Rss data has been imported from Database.")
