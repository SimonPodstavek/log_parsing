import os
from typing import Any

import psycopg2


class DatabaseCredentials:
    def __init__(self) -> None:
        self.user_set_login = False
        self.host = 'postgretst.postgres.database.azure.com'
        self.port = '5432'
        self.database = 'implementation_log'

        if "HMH_AZURE_LPT_USER" in os.environ:
            self.user = os.environ['HMH_AZURE_LPT_USER']
        else:
            self.user = input('User: ')
            self.user_set_login = True

        if "HMH_AZURE_LPT_PSSWD" in os.environ:
            self.password = os.environ['HMH_AZURE_LPT_PSSWD']
        else:
            self.password = input('Heslo: ')

        try:
            psycopg2.connect(
            host=self.host,port=self.port,database=self.database,user=self.user,password=self.password
        )
        except:
            print('Predovolené prihlasovacie údaje nie sú správne. Zadajte nové')
            self.host = input("Host: ")
            self.port = input("Port: ")
            self.database = input("Databáza: ")
            self.user = input('Používateľské meno: ')
            self.password = input('Používateľské heslo: ')
            print('Používateľské údaje nahradené')

    def __call__(self,super_user) -> tuple:
        if super_user and not self.user_set_login:
            self.user = input('Admin meno: ')
            self.password = input('Admin heslo: ')

        return {'host': self.host, 'port': self.port, 'database':self.database, 'user': self.user, 'password': self.password}

    



def create_session(SU=False):
    try:
        conn = psycopg2.connect(
            **(DatabaseCredentials()(SU))
        )
        cursor = conn.cursor()
        return cursor, conn
    except psycopg2.OperationalError  as err:
        print(f"Chyba 109: Pri vytváraní relácie medzi databázou a klientom sa vyskytla chyba.\n psycopg2: {err}")
        exit()
    else:
        print("Chyba 109: Pri vytváraní relácie medzi databázou a klientom sa vyskytla chyba.\n psycopg2: {e}")
        exit()

