from aiofiles.os import path as aiopath
from aioshutil import rmtree

from tghbot import (
    LOGGER,
    aria2_options,
    nzb_options,
    qbit_options,
    sabnzbd_client,
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
    no = (await sabnzbd_client.get_config())["config"]["misc"]
    nzb_options.update(no)


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
