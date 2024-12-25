from pyrogram import Client, filters  # type: ignore
from functions import adminPanel


@Client.on_message(filters.command(["admin", "panel", "adminPanel", "adminpanel"]))
async def handleAdminCommand(_, msg):
    text, keyboard = adminPanel(msg.from_user)
    await msg.reply(text, reply_markup=keyboard)
    pass
