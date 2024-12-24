import asyncio
import os
import sys
import subprocess
from config import SESSION, API_HASH, API_ID, BOT_TOKEN
from pyrogram import Client, idle  # type: ignore
from functions import temp


class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=500,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        try:
            if os.path.exists(SESSION+'.session'):
                os.remove(SESSION+'.session')
            await super().start()
            me = await self.get_me()
            temp.ME = me.id
            temp.U_NAME = me.username
            temp.B_NAME = me.first_name
            self.username = '@' + me.username
            print(f"Bot started!!!!!")
            print(
                f"""Bot Information:
Username: @{me.username}"""
            )
        except Exception as e:
            print(f"Error starting bot: {e}")
            raise e

    async def stop(self, *args):
        print('Stopping main bot............')
        await super().stop()
        sys.exit()


app = Bot()
app.run()
idle()
app.stop()
