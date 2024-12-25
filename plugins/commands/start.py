from pyrogram import Client, filters  # type: ignore
from database import Users
from middleware.checkUser import checkUser
from functions import mainMenu


@Client.on_message(filters.command('start'))
async def start(_, msg):
    if not await checkUser(_, msg):
        return
    text, keyboard = mainMenu(msg.from_user)
    await msg.reply(text, reply_markup=keyboard)
    pass
