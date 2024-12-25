from pyrogram import Client, filters  # type: ignore
from functions import adminManageAccounts, account_listings, account_details_view
from database import Accounts
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # type: ignore


@Client.on_callback_query(filters.regex(r'^/manageAccountAdmin'))
async def adminManageAccountsCallback(_, query):
    text, keyboard = await account_listings(query.from_user)
    await query.message.edit(text, reply_markup=keyboard)
    pass


@Client.on_callback_query(filters.regex(r'^/manageAccountListAdmin'))
async def adminManageAccountsListCallback(_, query):
    dataSplit = query.data.split(maxsplit=1)
    page = int(dataSplit[1]) if len(dataSplit) > 1 else 1
    text, keyboard = await adminManageAccounts(page)
    await query.message.edit(text, reply_markup=keyboard)
    pass


@Client.on_callback_query(filters.regex(r'^/viewAccount'))
async def adminViewAccount(_, query):
    appID = query.data.split(maxsplit=1)[1]
    accountDetails = Accounts.find_one({"appID": int(appID)})
    text, keyboard = await account_details_view(accountDetails)
    await query.message.edit(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^/remove_account'))
async def removeAccount(_, query):
    appID = query.data.split(maxsplit=1)[1]
    text = f"🚨 Are you sure you want to delete your account?\n\nAll your data will be permanently removed and cannot be recovered. This action is irreversible.\n\n<b>⚠️ Proceed with caution!</b>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", f"/cancelDeleteAccount {appID}"),
         InlineKeyboardButton("🗑️ Delete", f"/confirmRemoval {appID}")]
    ])
    await query.message.edit(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r'^/confirmRemoval'))
async def confirmAccountRemove(_, query):
    appID = query.data.split(maxsplit=1)[1]
    Accounts.delete_one({"appID": int(appID)})
    await query.message.edit(
        "✅ Account has been successfully deleted.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("↩️ Back to Listings",
                                   callback_data="/manageAccountListAdmin")]]
        )
    )


@Client.on_callback_query(filters.regex(r'^/cancelDeleteAccount'))
async def cancelDeleteAccount(_, query):
    appID = query.data.split(maxsplit=1)[1]
    accountDetails = Accounts.find_one({"appID": int(appID)})
    text, keyboard = await account_details_view(accountDetails)
    await query.message.edit(text, reply_markup=keyboard)
