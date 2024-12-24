from pyrogram import Client, filters  # type: ignore
from functions import botSettings
from middleware.authAdmin import authAdmin
from database import Admin


@Client.on_callback_query(filters.regex(r'^bot_settings'))
async def bot_settings(_, query):
    if not authAdmin(_, query):
        return
    text, keyboard = await botSettings(query.message.from_user)
    await query.message.edit(text, reply_markup=keyboard)
    pass


@Client.on_callback_query(filters.regex(r'^change_bot_status'))
async def changeBotStatus(_, query):
    if not authAdmin(_, query):
        return
    adminData = Admin.find_one({"admin": True}) or {}
    botStatus = adminData.get("bot_status", True)
    if botStatus:
        Admin.update_one({"admin": True}, {
                         "$set": {"bot_status": False}}, upsert=True)
    else:
        Admin.update_one({"admin": True}, {
                         "$set": {"bot_status": True}}, upsert=True)
    text, keyboard = await botSettings(query.message.from_user)
    await query.message.edit(text, reply_markup=keyboard)
    pass
