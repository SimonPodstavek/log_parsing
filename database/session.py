import os
from pymongo import MongoClient
import psycopg2



def create_session():
    try:
        conn=psycopg2.connect(
            host="postgretst.postgres.database.azure.com",
            port="5432",
            database="implementation_log",
            user="ovypt1",
            password=os.getenv("HMH_AZURE_LOG_PSSWD")
        )

        cursor = conn.cursor()
        return cursor, conn
    except:
        print("Chyba 109: Nepodarilo sa utvoriť reláciu medzi databázou a klientom.")
        exit()



#for mongoDB
# def create_session():
#     # cluster = "mongodb+srv://spodstavek:{}@cluster0.1ctzpcl.mongodb.net/implementation_log?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_PSSWD"))
#     cluster = "mongodb://localhost:27017"
#     client = MongoClient(cluster)
#     db = client.implementation_log
#     return db