from pyrogram import Client, filters, ContinuePropagation  # type: ignore
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton  # type: ignore
from .responseFunctions import checkIfTarget, createResponse, deleteResponse, getResponse
from config import cancelKeyboard, USERBOT_SESSION
from pyrogram.errors import PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded  # type: ignore
from database import Userbots, Accounts
from datetime import datetime
from functions import is_number , grantAccessMarkup
from orderAccounts import UserbotManager


# Fucntion to grant access to user
@Client.on_message(filters.private)
async def getUserIDToGrantAccess(_,message):
    if not checkIfTarget(message.from_user.id,"askUserIDForAccess"): raise ContinuePropagation()
    userID = message.text 
    if not is_number(userID):return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    text ,keyboard = await grantAccessMarkup(int(userID))
    await message.reply(text,reply_markup=keyboard)

# Function to vote in a pool
@Client.on_message(filters.private)
async def getPostLinkToVote(_,message):
    if not checkIfTarget(message.from_user.id,"postLinkToVote"): raise ContinuePropagation()
    postLink = str(message.text)
    if not postLink.startswith('https://'): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid url</b>")
    if postLink.startswith('https://t.me/c'): return await message.reply("<b>⚠️ Invalid input:  Please enter a public channel url</b>")
    deleteResponse(message.from_user.id)
    

#Functions to send reactions
@Client.on_message(filters.private)
async def getPostLinkToReact(_,message):
    if not checkIfTarget(message.from_user.id,"postLinkTosendReaction"): raise ContinuePropagation()
    postLink = str(message.text)
    if not postLink.startswith('https://'): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid url</b>")
    if postLink.startswith('https://t.me/c'): return await message.reply("<b>⚠️ Invalid input:  Please enter a public channel url</b>")
    deleteResponse(message.from_user.id)
    await message.reply("<b>👀 Enter Emoji to React:</b>")
    createResponse(message.from_user.id,"emojiToSendReaction",{"postLink":postLink})
    
@Client.on_message(filters.private)
async def getEmojiToReact(_,message):
    if not checkIfTarget(message.from_user.id,"emojiToSendReaction"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    emojiToReact = message.text 
    deleteResponse(message.from_user.id)
    await message.reply("<b>👀 Enter The No. Of Reactions:</b>")
    
    createResponse(message.from_user.id,"numberOfReactionsOnPost",{**responseData,"emoji":emojiToReact})

@Client.on_message(filters.private)
async def getNumberOfReactionsOnPost(_,message):
    if not checkIfTarget(message.from_user.id,"numberOfReactionsOnPost"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    numberOFViews = message.text 
    if (not is_number(numberOFViews)) or (float(numberOFViews) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    await message.reply("⚡️ Choose The Speed Of The Work: ( In Seconds )\n• Enter Or Choose From The Keyboard\n0 = All The Views Come Instantly.\n1 = Each 1 Second 1 View\n60 = Each 1 Minute 1 View")
    createResponse(message.from_user.id,"askSpeedOFReactions",{**responseData,"numberOfReactions":int(numberOFViews)})
    
@Client.on_message(filters.private)
async def askSpeedOFReactionsHandler(_,message):
    if not checkIfTarget(message.from_user.id,"askSpeedOFReactions"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    seconds = message.text 
    if (not is_number(seconds)) or (float(seconds) < 0): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    userBots = list(Accounts.find({}).limit(int(responseData.get("numberOfReactions"))))
    await message.reply("<b>📋 Executing The Task...</b>")
    print(responseData)
    await UserbotManager.bulk_order(userBots,{
        "type":"reactPost",
        "postLink": responseData.get("postLink"),
        "restTime":float(seconds),
        "taskPerformCount": int(responseData.get("numberOfReactions")),
        "emoji":responseData.get("emoji")
    })
    await message.reply(f"<b>✅ Task Executed: {len(userBots)} Accounts</b>")

#Function to send views
@Client.on_message(filters.private)
async def getPostLinkToSendViews(_,message):
    if not checkIfTarget(message.from_user.id,"postLinkTosendViews"): raise ContinuePropagation()
    postLink = str(message.text)
    if not postLink.startswith('https://'): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid url</b>")
    if postLink.startswith('https://t.me/c'): return await message.reply("<b>⚠️ Invalid input:  Please enter a public channel url</b>")
    deleteResponse(message.from_user.id)
    await message.reply("<b>👀 Enter The No. Of Views:</b>")
    createResponse(message.from_user.id,"numberOfViewsOnPost",{"postLink":postLink})
    
@Client.on_message(filters.private)
async def getNumberOfViewsOnPost(_,message):
    if not checkIfTarget(message.from_user.id,"numberOfViewsOnPost"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    numberOFViews = message.text 
    if (not is_number(numberOFViews)) or (float(numberOFViews) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    await message.reply("⚡️ Choose The Speed Of The Work: ( In Seconds )\n• Enter Or Choose From The Keyboard\n0 = All The Views Come Instantly.\n1 = Each 1 Second 1 View\n60 = Each 1 Minute 1 View")
    createResponse(message.from_user.id,"askSpeedOFViews",{**responseData,"numberOfViews":int(numberOFViews)})
    
@Client.on_message(filters.private)
async def askSpeedOFviewsHandler(_,message):
    if not checkIfTarget(message.from_user.id,"askSpeedOFViews"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    seconds = message.text 
    if (not is_number(seconds)) or (float(seconds) < 0): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    userBots = list(Accounts.find({}).limit(int(responseData.get("numberOfViews"))))
    await message.reply("<b>📋 Executing The Task...</b>")
    await UserbotManager.bulk_order(userBots,{
        "type":"viewPosts",
        "postLink": responseData.get("postLink"),
        "restTime":float(seconds),
        "taskPerformCount": int(responseData.get("numberOfViews"))
    })
    await message.reply(f"<b>✅ Task Executed: {len(userBots)} Accounts</b>")

#Leave Channels Functions
@Client.on_message(filters.private)
async def getChatIDtoleave(_,message):
    if not checkIfTarget(message.from_user.id,"leaveChatID"): raise ContinuePropagation()
    chatID = message.text 
    chatIDArray = chatID.split("|")
    deleteResponse(message.from_user.id)
    await message.reply("<b>❓ How Many Members You Want To Leave?</b>")
    createResponse(message.from_user.id,"leaveChatMembersCount",{"chatIDs":chatIDArray})
    
    
@Client.on_message(filters.private)
async def getleaveMembersCount(_,message):
    if not checkIfTarget(message.from_user.id,"leaveChatMembersCount"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    membersCount = message.text 
    if (not is_number(membersCount)) or (float(membersCount) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    createResponse(message.from_user.id,"askForSpeedOfLeave",{**responseData,"membersCount":int(membersCount)})
    await message.reply(
        "<b>⚡️ Choose The Speed Of The Work: (In Seconds)\n"
        "• 0 = All the members leave Instant.\n"
        "• 1 = Add 1 member every 1 second.\n"
        "• 60 = Add 1 member every 1 minute.</b>")
    
@Client.on_message(filters.private)
async def askForSpeedOfleaveHandler(_,message):
    if not checkIfTarget(message.from_user.id,"askForSpeedOfLeave"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    seconds = message.text
    if (not is_number(seconds)) or (float(seconds) < 0): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    userBots = list(Accounts.find({}).limit(int(responseData.get("membersCount"))))
    await message.reply("<b>📋 Executing The Task...</b>")
    await UserbotManager.bulk_order(userBots,{
        "type":"leave_channel",
        "channels": responseData.get("chatIDs"),
        "restTime":float(seconds),
        "taskPerformCount": int(responseData.get("membersCount"))
    })
    await message.reply(f"<b>✅ Task Executed: {len(userBots)} Accounts</b>")

#Join Channel Functions
@Client.on_message(filters.private)
async def getChatIDtoJoin(_,message):
    if not checkIfTarget(message.from_user.id,"joinChatID"): raise ContinuePropagation()
    chatID = message.text 
    chatIDArray = chatID.split("|")
    deleteResponse(message.from_user.id)
    await message.reply("<b>❓ How Many Members Need?</b>")
    createResponse(message.from_user.id,"joinChatMembersCount",{"chatIDs":chatIDArray})
    
    
@Client.on_message(filters.private)
async def getJoinMembersCount(_,message):
    if not checkIfTarget(message.from_user.id,"joinChatMembersCount"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    membersCount = message.text 
    if (not is_number(membersCount)) or (float(membersCount) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    createResponse(message.from_user.id,"askForSpeedOfJoin",{**responseData,"membersCount":int(membersCount)})
    await message.reply(
        "<b>⚡️ Choose The Speed Of The Work: (In Seconds)\n"
        "• 0 = All the members added Instant.\n"
        "• 1 = Add 1 member every 1 second.\n"
        "• 60 = Add 1 member every 1 minute.</b>")
    
@Client.on_message(filters.private)
async def askForSpeedOfJoinHandler(_,message):
    if not checkIfTarget(message.from_user.id,"askForSpeedOfJoin"): raise ContinuePropagation()
    responseData = getResponse(message.from_user.id).get("payload")
    seconds = message.text
    if (not is_number(seconds)) or (float(seconds) < 0): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    userBots = list(Accounts.find({}).limit(int(responseData.get("membersCount"))))
    await message.reply("<b>📋 Executing The Task...</b>")
    await UserbotManager.bulk_order(userBots,{
        "type":"join_channel",
        "channels": responseData.get("chatIDs"),
        "restTime":float(seconds),
        "taskPerformCount": int(responseData.get("membersCount"))
    })
    await message.reply(f"<b>✅ Task Executed: {len(userBots)} Accounts</b>")


@Client.on_message(filters.private)
async def getMessageToSendHandler(_,message):
    if not checkIfTarget(message.from_user.id,"messageToSend"): raise ContinuePropagation()
    try:
        text = str(message.text)
        textArray = text.split("|")
        textArray = [message.strip() for message in textArray]
        if len(textArray) < 5: return await message.reply("<b>❌ Please enter at least 5 unique messages to continue.</b>")
        deleteResponse(message.from_user.id)
        await message.reply("📩 Send the username of the person you want to send messages.")
        createResponse(message.from_user.id,"messageDeliverChatID",{"text":textArray})
    except Exception as e:
        raise e
    
@Client.on_message(filters.private)
async def getMessageDeliverIDHandler(_,message):
    if not checkIfTarget(message.from_user.id,"messageDeliverChatID"): raise ContinuePropagation
    responseData = getResponse(message.from_user.id).get("payload")
    chatID = message.text 
    deleteResponse(message.from_user.id)
    createResponse(message.from_user.id,"askForMessagesCount",{**responseData,"chatID":chatID})
    await message.reply("❓ How many messages do you want to send?")
    
@Client.on_message(filters.private)
async def askForMessagesCountHandler(_,message):
    if not checkIfTarget(message.from_user.id,"askForMessagesCount"): raise ContinuePropagation
    responseData = getResponse(message.from_user.id).get("payload")
    messagesCount = message.text 
    if (not is_number(messagesCount)) or (float(messagesCount) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    createResponse(message.from_user.id,"askForSpeedOfWork",{**responseData,"messagesCount":int(messagesCount)})
    await message.reply(
        "<b>⚡️ Enter The Speed Of The Work: ( In Seconds )</b>"
        "0 = All The Message Comes in Instantly Second."
        "1 = Each 1 Second 1 Message"
        "60 = Each 1 Minute 1 Message"
    )
    pass

@Client.on_message(filters.private)
async def askForSpeedOfWork(_,message):
    if not checkIfTarget(message.from_user.id,"askForSpeedOfWork"): raise ContinuePropagation
    responseData = getResponse(message.from_user.id).get("payload")
    seconds = message.text 
    if (not is_number(seconds)) or (float(seconds) < 1): return await message.reply("<b>⚠️ Invalid input:  Please enter a valid value</b>")
    deleteResponse(message.from_user.id)
    userBots = list(Accounts.find({}).limit(int(responseData.get("messagesCount"))))
    await message.reply("<b>📋 Executing The Task...</b>")
    await UserbotManager.bulk_order(userBots,{
        "type": "sendMessage",
        "chatID":responseData.get("chatID"),
        "text":responseData.get("text"),
        "restTime":float(seconds),
        "taskPerformCount": int(responseData.get("messagesCount"))
    })
    await message.reply(f"<b>✅ Task Executed: {len(userBots)} Accounts</b>")



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
            "userbot_client": userbot_client, "app_id": app_id,"app_hash":app_hash,"phone":phone_number
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