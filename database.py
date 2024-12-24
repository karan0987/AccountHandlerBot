from pymongo import MongoClient  # type: ignore
from config import MONGO_URL


try:
    client = MongoClient(MONGO_URL)
    mydb = client['AccountHandlerBot']
    Userbots = mydb['userbots']
    Admin = mydb['admin']
    Users = mydb['users']
    Accounts = mydb['accounts']
    Transactions = mydb["Transactions"]
except Exception as e:
    print("Error connecting to MongoDB: ", e)
