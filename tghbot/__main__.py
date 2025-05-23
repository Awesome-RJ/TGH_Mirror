# ruff: noqa: E402
import asyncio

from pyrogram.types import BotCommand

from tghbot import LOGGER, bot_loop
from tghbot.core.config_manager import Config, SystemEnv
from tghbot.core.startup import load_settings
from tghbot.core.tgh_client import TgClient
from tghbot.helper.telegram_helper.bot_commands import BotCommands

# Initialize Configurations
LOGGER.info("Loading configurations...")
Config.load()
SystemEnv.load()

# Load initial settings asynchronously
bot_loop.run_until_complete(load_settings())

# Define Bot Commands and Descriptions
# This dictionary maps internal command names to their user-facing descriptions.
# The keys are typically attributes from BotCommands, and values are short descriptions.
COMMANDS_INFO = {
    "MirrorCommand": "- Start mirroring",
    "LeechCommand": "- Start leeching",
    "JdMirrorCommand": "- Mirror using Jdownloader",
    "JdLeechCommand": "- Leech using jdownloader",
    "NzbMirrorCommand": "- Mirror nzb files",
    "NzbLeechCommand": "- Leech nzb files",
    "YtdlCommand": "- Mirror yt-dlp supported link",
    "YtdlLeechCommand": "- Leech through yt-dlp supported link",
    "CloneCommand": "- Copy file/folder to Drive",
    "MediaInfoCommand": "- Get mediainfo",
    "ForceStartCommand": "- Start task from queue",
    "CountCommand": "- Count file/folder on Google Drive",
    "ListCommand": "- Search in Drive",
    "SearchCommand": "- Search in Torrent",
    "UserSetCommand": "- User settings",
    "StatusCommand": "- Get mirror status message",
    "StatsCommand": "- Check Bot & System stats",
    "CancelAllCommand": "- Cancel all tasks added by you to the bot",
    "HelpCommand": "- Get detailed help",
    "SpeedTest": "- Get speedtest result",
    "BotSetCommand": "- [ADMIN] Open Bot settings",
    "LogCommand": "- [ADMIN] View log",
    "RestartCommand": "- [ADMIN] Restart the bot",
    # "RestartSessionsCommand": "- [ADMIN] Restart the session instead of the bot", # Commented out as in original
}


# Prepare BotCommand objects for Telegram
COMMAND_OBJECTS = []
for cmd, description in COMMANDS_INFO.items():
    # Retrieve the command name from BotCommands, handling both single string and list formats
    command_name = getattr(BotCommands, cmd)
    if isinstance(command_name, list):
        command_name = command_name[0]
    COMMAND_OBJECTS.append(BotCommand(command_name, description))


async def set_bot_commands():
    """Sets the bot commands on Telegram if SET_COMMANDS is enabled in config."""
    if Config.SET_COMMANDS:
        LOGGER.info("Setting bot commands on Telegram...")
        await TgClient.bot.set_bot_commands(COMMAND_OBJECTS)
        LOGGER.info("Bot commands set successfully.")
    else:
        LOGGER.info("SET_COMMANDS is disabled. Skipping bot command setup.")


async def main():
    """Main asynchronous function to start the bot and initialize necessary components."""
    from tghbot.core.jdownloader_booter import jdownloader
    from tghbot.core.startup import (
        load_configurations,
        save_settings,
        update_aria2_options,
        update_nzb_options,
        update_qb_options,
        update_variables,
    )
    from tghbot.core.torrent_manager import TorrentManager
    from tghbot.helper.ext_utils.files_utils import clean_all
    from tghbot.helper.ext_utils.telegraph_helper import telegraph
    from tghbot.helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
    from tghbot.modules import (
        get_packages_version,
        initiate_search_tools,
        restart_notification,
    )

    LOGGER.info("Starting Telegram clients...")
    await asyncio.gather(TgClient.start_bot(), TgClient.start_user())
    LOGGER.info("Telegram clients started.")

    LOGGER.info("Loading configurations and updating variables...")
    await asyncio.gather(load_configurations(), update_variables())

    LOGGER.info("Initializing TorrentManager...")
    await TorrentManager.initiate()

    LOGGER.info("Updating qBittorrent, Aria2, and NZB options...")
    await asyncio.gather(
        update_qb_options(),
        update_aria2_options(),
        update_nzb_options(),
    )

    LOGGER.info("Performing essential startup tasks...")
    await asyncio.gather(
        set_bot_commands(),
        jdownloader.boot(),
    )

    LOGGER.info("Performing additional startup tasks and cleanups...")
    await asyncio.gather(
        save_settings(),
        clean_all(),
        initiate_search_tools(),
        get_packages_version(),
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
    )
    LOGGER.info("All startup tasks completed.")


# Run the main function to start the bot and its services
bot_loop.run_until_complete(main())

# Import and add handlers after initial setup is complete
from tghbot.core.handlers import add_handlers
from tghbot.helper.ext_utils.bot_utils import create_help_buttons
from tghbot.helper.listeners.aria2_listener import add_aria2_callbacks

LOGGER.info("Adding Aria2 callbacks...")
add_aria2_callbacks()

LOGGER.info("Creating help buttons...")
create_help_buttons()

LOGGER.info("Adding general bot handlers...")
add_handlers()

# Start the bot's event loop
LOGGER.info("Bot Started!")
bot_loop.run_forever()
