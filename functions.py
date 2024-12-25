import time
import asyncio
import pytz
from pyrogram import Client,filters #type: ignore
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton #type: ignore
from database import Users , Accounts, Admin
import asyncio
from datetime import datetime

timezone = pytz.timezone("Asia/Kolkata") 


class temp(object):
    ME = None
    CANCEL = False
    CURRENT = 0
    
    
    
def mainMenu(fromUser):
    text =  (f"<b>👋 Hello, {fromUser.first_name}!</b>\n\n")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Send Message","/sendMessage")],
        [InlineKeyboardButton("🔔 Join Chat","/joinChats"),InlineKeyboardButton("🔕 Leave Chats","/leaveChats")],
        [InlineKeyboardButton("👀 Views","/sendViews"),InlineKeyboardButton("❤️ Reaction","/sendReactions")],
        # [InlineKeyboardButton("🗳 Votes","/sendVotes")]
        ])
    return text,keyboard


#For admin
async def grantAccessMarkup(userID):
    accessUsers = Admin.find_one({"accessUser":True}) or {}
    usersList = accessUsers.get("list",[])
    text = f"<b>UserID: </b><code>{userID}</code>"
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Grant Access" if (not int(userID) in usersList) else "❎ Remove Access",f"/changeAccess {userID}")]
        ]
    )
    return text, keyboard

# For Admin
def adminPanel(fromUser):
    text = "<b>Welcome, Admin!\nSelect a section to manage the bot and its users.</b>"
    keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("⚙️ Grant Access", callback_data="/grantAccess")],
    [InlineKeyboardButton("📋 Telegram Accounts", callback_data="/manageAccountAdmin")],
    ])
    return text,keyboard



# For Admin
async def adminManageAccounts(page: int = 1, per_page: int = 5):
    allAccounts = list(Accounts.find({}))
    total_accounts = len(allAccounts)
    if total_accounts == 0:
        text = (
            f"{"<b>No accounts created yet.<b>"}"
            )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back To Menu", callback_data=f"admin")]]
        )
        return text, keyboard

    # Pagination logic
    start = (page - 1) * per_page
    end = start + per_page
    accounts_to_display = allAccounts[start:end]
    total_pages = (total_accounts + per_page - 1) // per_page  # Calculate total pages

    # Navigation buttons
    keyboard_buttons = []
    # Construct the message text
    text = f"<b>Manage Accounts (Page {page}/{total_pages}):</b>\n\n"
    for i, account in enumerate(accounts_to_display, start=start + 1):
        keyboard_buttons.append(InlineKeyboardButton(f"{i}. {account.get('appID')}",f"/viewAccount {account.get('appID')}"))
        account_info = (
            f"<b>🔹 Account {i}:</b>\n"
            f"<b>Username:</b> <code>{account.get('username', 'N/A')}</code>\n"
            f"<b>App ID: {account.get('appID','N/A')}</b>"
        )
        text += account_info

    #Navigation Button 
    navigationButton = []
    if page > 1:
        navigationButton.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"/account_listings {page - 1}"))
    if page < total_pages:
        navigationButton.append(InlineKeyboardButton("Next ➡️", callback_data=f"/account_listings {page + 1}"))

    # Back button
    backButton = [InlineKeyboardButton("🔙 Back To Menu", callback_data=f"admin")]
    keyboard = InlineKeyboardMarkup([keyboard_buttons,navigationButton,backButton])

    return text, keyboard


# For Admin
async def account_listings(fromUser):
    text = "<b>📋 Manage Telegram Accounts</b>\n\nHere, you can manage all Telegram accounts available for sale.\n\nChoose an option below to proceed."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 View All Accounts",
                              callback_data="/manageAccountListAdmin")],
        [InlineKeyboardButton("➕ Add New Account",
                              callback_data="/add_account")],
        [InlineKeyboardButton("🔙 Back To Menu", callback_data="admin")]
    ])
    
    return text, keyboard

#For Admin
async def account_details_view(account_info,backCommand="/manageAccountListAdmin",langCode="english"):
    # Display account details
    text = (
        "<b>🔍 Account Details</b>\n\n"
        f"<b>App ID: </b><code>{account_info.get('appID')}</code>\n"
        f"<b>App Hash: </b><code>{account_info.get('appHash')}</code>\n"
        f"<b>Phone Number: </b><code>{account_info['phone_number']}</code>\n"
        f"<b>Username: <a href='https://t.me/{account_info.get('username')}'>{account_info.get('username')}</a></b>\n"
        f"<b>Created AT: </b><code>{convertTime(account_info.get('added_at'))}</code>\n"
        "Choose an action for this account."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("↩️ Back",callback_data=backCommand)],
        [InlineKeyboardButton("🗑️ Remove Account", callback_data=f"/remove_account {account_info['appID']}")],
    ])
    
    return text, keyboard


def is_number(value):
    if isinstance(value, (int, float)):return True
    if isinstance(value, str):
        try:
            float(value) 
            return True
        except ValueError:return False
    return False




def convertTime(timestamp):
    if isinstance(timestamp, datetime): utc_time = timestamp
    else: utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    utc_time = pytz.utc.localize(utc_time)
    local_time = utc_time.astimezone(timezone)
    readable_format = local_time.strftime("%Y-%m-%d %I:%M:%S %p")
    return readable_format
