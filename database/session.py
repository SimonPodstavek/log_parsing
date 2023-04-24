import os
from pymongo import MongoClient


def create_session():
    #127.0.0.1
    cluster = "mongodb://localhost:27017"


    #Atlas
    # cluster = "mongodb+srv://spodstavek:{}@cluster0.1ctzpcl.mongodb.net/implementation_log?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_PSSWD"))
    
    #Azure
    # cluster = "mongodb://free-test:{}@free-test.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@free-test@".format(os.getenv("AZURE_MONGO_LOG_PSSWH"))
    client = MongoClient(cluster)
    db = client.implementation_log
    return db

# test chan