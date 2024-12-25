from pyrogram import Client, filters  # type: ignore
from functions import mainMenu


@Client.on_callback_query(filters.regex("/main_menu"))
async def main_Menu(_, query):
    text, keyboard = mainMenu(query.from_user)
    await query.message.edit(text, reply_markup=keyboard)