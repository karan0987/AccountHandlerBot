from pyrogram import Client , filters 
from config import cancelKeyboard
from ..responses.responseFunctions import createResponse


@Client.on_callback_query(filters.regex(r'^/sendMessage'))
async def sendMessageHandler(_,query):
    await query.message.edit(f"📝 Enter The Message",reply_markup=cancelKeyboard)
    createResponse(query.from_user.id,"messageToSend")