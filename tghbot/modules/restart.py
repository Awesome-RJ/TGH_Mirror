import os
import sys

from pyrogram import Client, filters

from tghbot.core.tgh_client import TgClient
from tghbot.helper.ext_utils.bot_utils import new_task
from tghbot.helper.telegram_helper.message_utils import send_message

# List of user IDs allowed to restart the bot
SUDO_USERS = [123456789, 987654321]  # Replace with actual user IDs

app = Client("tghbot")


@app.on_message(filters.command("restart") & filters.user(SUDO_USERS))
@new_task
async def restart_bot(client, message):
    try:
        await send_message(message, "🔄 Restarting bot...")
        # Restart the bot
        os.execv(sys.executable, ["python", *sys.argv])
    except Exception as e:
        await send_message(message, f"Error: {e}")


if __name__ == "__main__":
    app.run()
