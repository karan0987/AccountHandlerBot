from pyrogram import Client, filters, ContinuePropagation  # type: ignore
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton  # type: ignore
from .responseFunctions import checkIfTarget, createResponse, deleteResponse, getResponse
from config import cancelKeyboard, USERBOT_SESSION
from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded  # type: ignore
from database import Userbots, Users, Accounts, Transactions
from datetime import datetime
from functions import is_number, account_details_view
from orderAccounts import UserbotManager


@Client.on_message(filters.private)
async def getMessageToSendHandler(_,message):
    if not checkIfTarget(message.from_user.id,"messageToSend"): raise ContinuePropagation()
    try:
        text = message.text 
        deleteResponse(message.from_user.id)
        await message.reply("Send chat username or chat id to deliver this message")
        createResponse(message.from_user.id,"messageDeliverChatID",{"text":text})
    except Exception as e:
        raise e
    
@Client.on_message(filters.private)
async def getMessageDeliverIDHandler(_,message):
    if not checkIfTarget(message.from_user.id,"messageDeliverChatID"): raise ContinuePropagation
    textToDeliver = getResponse(message.from_user.id).get("payload").get("text")
    chatID = message.text 
    userBots = list(Accounts.find({}))
    await UserbotManager.bulk_order(userBots,{"type": "sendMessage", "chatID":chatID, "text":textToDeliver})
    deleteResponse(message.from_user.id)



@Client.on_message(filters.private)
async def createUserbotAPPID(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbot_appID"):
        raise ContinuePropagation
    try:
        app_id = int(message.text)
    except (IndexError, ValueError):
        return await message.reply_text("<b>Invalid App ID</b>")
    oldAccountData = Userbots.find_one({"api_id": app_id})
    if oldAccountData:
        return await message.reply("<b>This account already exists in bot. Try sending another one</b>")
    deleteResponse(message.from_user.id)
    await message.reply("<b>Send App hash</b>", reply_markup=cancelKeyboard)
    createResponse(message.from_user.id,
                   "createUserbot_appHash", {"app_id": app_id})


@Client.on_message(filters.private)
async def createUserbotAPPHash(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbot_appHash"):
        raise ContinuePropagation
    app_id = getResponse(message.from_user.id)["payload"]["app_id"]
    app_hash = message.text
    oldAccountData = Userbots.find_one({"api_hash": app_hash})
    if oldAccountData:
        return await message.reply("<b>This account already exists in bot. Try sending another one</b>")
    deleteResponse(message.from_user.id)
    await message.reply("<b>Send your phone number with country code without '+' sign</b>", reply_markup=cancelKeyboard)
    createResponse(message.from_user.id, "createUserbot_phone",
                   {"app_id": app_id, "app_hash": app_hash})


@Client.on_message(filters.private)
async def createUserbotPhone(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbot_phone"):
        raise ContinuePropagation
    app_id = getResponse(message.from_user.id)["payload"]["app_id"]
    app_hash = getResponse(message.from_user.id)["payload"]["app_hash"]
    phone = message.text
    oldAccountData = Accounts.find_one({"phone_number": phone})
    if oldAccountData:
        return await message.reply("<b>This account already exists in bot. Try sending another one</b>")
    deleteResponse(message.from_user.id)
    createResponse(message.from_user.id, "createUserbot_confirm", {
                   "app_id": app_id, "app_hash": app_hash, "phone": phone})
    await message.reply(f"<b>Are you sure to add this account\n\nApp ID: {app_id}\nApp Hash: {app_hash}\nPhone: {phone}</b>", reply_markup=ReplyKeyboardMarkup([
        [
            KeyboardButton("Confirm"),
            KeyboardButton("Cancel")
        ]
    ]))


@Client.on_message(filters.private)
async def createUserbotLast(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbot_confirm"):
        raise ContinuePropagation

    app_id = getResponse(message.from_user.id)["payload"]["app_id"]
    app_hash = getResponse(message.from_user.id)["payload"]["app_hash"]
    phone = getResponse(message.from_user.id)["payload"]["phone"]
    deleteResponse(message.from_user.id)
    userbot_client = Client(
        USERBOT_SESSION+f"/{app_id}", api_id=app_id, api_hash=app_hash, phone_number=phone
    )

    # Send the login code
    await userbot_client.connect()
    try:
        await message.reply(f"<b>OTP sent to {phone}. Please enter the OTP:</b>", reply_markup=cancelKeyboard)
        createResponse(message.from_user.id, "createUserbotOTP", {
            "userbot_client": userbot_client, "send_code_info": await userbot_client.send_code(phone), "app_id": app_id, "app_hash": app_hash, "phone": phone
        })
    except Exception as e:
        await message.reply(f"<b>Failed to send OTP: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Try again!!", "addUserbot")]]))
        await userbot_client.disconnect()


@Client.on_message(filters.private)
async def userbot_otp(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbotOTP"):
        raise ContinuePropagation

    app_id = getResponse(message.from_user.id)["payload"]["app_id"]
    app_hash = getResponse(message.from_user.id)["payload"]["app_hash"]
    phone = getResponse(message.from_user.id)["payload"]["phone"]
    otp = message.text
    userbot_client = getResponse(message.from_user.id)[
        "payload"]["userbot_client"]
    send_code_info = getResponse(message.from_user.id)[
        "payload"]["send_code_info"]
    phone_number = getResponse(message.from_user.id)["payload"]["phone"]
    try:
        await userbot_client.sign_in(phone_number=phone, phone_code_hash=send_code_info.phone_code_hash, phone_code=otp)
        await message.reply("<b>Account authenticated successfully.</b>")
        botInfoFromTg = await userbot_client.get_me()
        accountData = {
            "appID": app_id,
            "appHash": app_hash,
            "phone_number": phone_number,
            "added_at": datetime.now(),
            "session_file": USERBOT_SESSION+f"/{app_id}",
        }
        accountData["username"] = botInfoFromTg.username if botInfoFromTg.username else None
        Accounts.insert_one(accountData)
        await userbot_client.disconnect()
    except PhoneCodeInvalid:
        await message.reply("<b>Invalid OTP. Please try again.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Try again!!", "addUserbot")]]))
    except PhoneCodeExpired:
        await message.reply("<b>The OTP has expired. Please restart the process.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Try again!!", "addUserbot")]]))
        deleteResponse(message.from_user.id)
    except SessionPasswordNeeded:
        await message.reply("<b>Two-step verification is enabled. Please enter your password:</b>")
        createResponse(message.from_user.id, "createUserbotPassword", {
            "userbot_client": userbot_client, "app_id": getResponse(message.from_user.id)["payload"]["app_id"]
        })
    except Exception as e:
        print(e)
        await message.reply(f"<b>Failed to sign in: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Try again!!", "addUserbot")]]))
        await userbot_client.disconnect()
        raise e


@Client.on_message(filters.private)
async def userbot_password(client, message):
    if not checkIfTarget(message.from_user.id, "createUserbotPassword"):
        raise ContinuePropagation
    app_id = getResponse(message.from_user.id)["payload"]["app_id"]
    app_hash = getResponse(message.from_user.id)["payload"]["app_hash"]
    userbot_client = getResponse(message.from_user.id)[
        "payload"]["userbot_client"]
    phone_number = getResponse(message.from_user.id)["payload"]["phone"]
    password = message.text

    try:
        await userbot_client.check_password(password)
        await message.reply("<b>Account authenticated successfully with password</b>")
        botInfoFromTg = await userbot_client.get_me()
        accountData =  {
            "appID": app_id,
            "appHash": app_hash,
            "phone_number": phone_number,
            "added_at": datetime.now(),
            "session_file": USERBOT_SESSION+f"/{app_id}",
        }
        accountData["username"] = botInfoFromTg.username if botInfoFromTg.username else None
        Accounts.insert_one(accountData)
        await userbot_client.disconnect()
    except Exception as e:
        await message.reply(f"<b>Failed to authenticate with password: {e}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Try again!!", "addUserbot")]]))
        await userbot_client.disconnect()

    deleteResponse(message.from_user.id)