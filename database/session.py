import os
from pymongo import MongoClient
import psycopg2



def create_session():
    conn=psycopg2.connect(
        host="postgretst.postgres.database.azure.com",
        port="5432",
        database="implementation_log",
        user="ovypt1",
        password=os.getenv("HMH_AZURE_LOG_PSSWD"),
    )
    
    cursor = conn.cursor()
    paths=cursor.execute("SELECT * FROM Path")
    actors=cursor.execute("SELECT * FROM Actor")
    boards=cursor.execute("SELECT * FROM Board")
    HDV=cursor.execute("SELECT * FROM HDV")
    software=cursor.execute("SELECT * FROM Software")

    cursor.fetchall()

    cursor.close()
    conn.close()

#for mongoDB
# def create_session():
#     # cluster = "mongodb+srv://spodstavek:{}@cluster0.1ctzpcl.mongodb.net/implementation_log?retryWrites=true&w=majority".format(os.getenv("HMH_MONGO_LOG_PSSWD"))
#     cluster = "mongodb://localhost:27017"
#     client = MongoClient(cluster)
#     db = client.implementation_log
#     return db