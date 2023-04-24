import os
from pymongo import MongoClient


def create_session():
    cluster = "mongodb+srv://spodstavek:{}@cluster0.1ctzpcl.mongodb.net/implementation_log?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_PSSWD"))
    client = MongoClient(cluster)
    db = client.implementation_log
    return db

# test chan