import os
from pymongo import MongoClient


def create_session():
    # cluster = "mongodb+srv://spodstavek:{}@cluster0.1ctzpcl.mongodb.net/implementation_log?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_PSSWD"))
    cluster = "mongodb://free-test:ehSAYoTO8OkUXCTmxfUe5vOzgXdaZavkPpJ1CBaY1BkF4sIKd3pUFbr88EPm3CFPYrof9sCJgqq8ACDbMR67sg==@free-test.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@free-test@"
    client = MongoClient(cluster)
    db = client.implementation_log
    return db