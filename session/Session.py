import psycopg2

import os



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
    except psycopg2.OperationalError  as err:
        print(f"Chyba 109: Nepodarilo sa utvoriť reláciu medzi databázou a klientom.\n psycopg2: {err}")
        exit()
    else:
        print("Chyba 109: Nepodarilo sa utvoriť reláciu medzi databázou a klientom.\n psycopg2: {e}")
        exit()