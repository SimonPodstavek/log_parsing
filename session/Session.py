import os
from typing import Any
from msvcrt import getch
from getpass import getpass

import psycopg2
from psycopg2 import sql


class InsufficientPrivilegesException(Exception):
    pass


def verify_privileges(privileges_requirements: set, user:str, conn) -> bool:
    cursor = conn.cursor()
    query = sql.SQL('SELECT \"privilege_type\" FROM information_schema.role_table_grants WHERE \"grantee\" = {grantee} GROUP BY "privilege_type"').format(grantee=sql.Literal(user))
    cursor.execute(query)

    if len(privileges_requirements - {privilege[0] for privilege in cursor.fetchall()}) == 0:
        return True
    else:
        return False







class DatabaseCredentials:
    def __init__(self) -> None:
        self.host = 'postgretst.postgres.database.azure.com'
        self.port = '5432'
        self.database = 'implementation_log'
        self.user = None
        self.password = None
        self.is_admin = False
        self.privileges = {'SELECT', 'INSERT'}


        if "HMH_AZURE_LPT_USER" in os.environ:
            self.user = os.environ['HMH_AZURE_LPT_USER']

        if "HMH_AZURE_LPT_PSSWD" in os.environ:
            self.password = os.environ['HMH_AZURE_LPT_PSSWD']


    def __call__(self,super_user) -> tuple:
        if super_user and not self.is_admin:
            self.user = input('Admin meno: ')
            self.password = input('Admin heslo: ')
            self.privileges = {'SELECT', 'DELETE', 'INSERT', 'UPDATE'}
            self.is_admin = True

        if self.user is None or self.password is None:
            print('Zadajte prihlasovacie údaje do databázy:')
            if self.user is None:
                self.user = input('DB používateľ: ')

            if self.password is None:
                self.password = input('DB heslo: ')




        #verify that the inputed / default credentials can be used to initiate relation
        def verify_connectivity():
            try:
                conn = psycopg2.connect(
                host=self.host,port=self.port,database=self.database,user=self.user,password=self.password)
                conn.autocommit = False

                # Verify wheather the user has sufficeint privileges for the selected operation
                if not verify_privileges(self.privileges, self.user, conn):
                    raise InsufficientPrivilegesException
            

                return conn
            
            except InsufficientPrivilegesException:
                print(f'Chyba 127: Iniciácia relácie prebehla úspešne, prihlásený používateľ nemá dostatočné povolenia. Chcete sa prihlásiť ako iný používateľ: (Y/N)')
                if getch().lower() != b'y':
                    print(f"Chyba 126: Nebolo možné vytvoriť reláciu medzi databázou a klientom z dôvodu nenahradenia chybných údajov.\nUkončujem aplikáciu.")
                    exit() 

                self.user = input('DB Admin: ')
                self.password = input('DB Heslo: ')
                return verify_connectivity()
                
            except Exception:
                print('Prihlasovacie údaje nie sú správne. Chcete zadať nové: (Y/N)')
                
                if getch().lower() != b'y':
                    print(f"Chyba 126: Nebolo možné vytvoriť reláciu medzi databázou a klientom z dôvodu nenahradenia chybných údajov.\nUkončujem aplikáciu.")
                    exit()

                self.host = input("Host: ")
                self.port = input("Port: ")
                self.database = input("Databáza: ")
                self.user = input('DB používateľ: : ')
                self.password = input('DB heslo: ')
                return verify_connectivity()

        return verify_connectivity()
    

    
ini_database_credentials = DatabaseCredentials()


def create_session(SU=False):
    try:
        conn = ini_database_credentials(SU)
        cursor = conn.cursor()
        return cursor, conn
    except Exception  as err:
        print(f'Chyba 109: Pri vytváraní relácie medzi databázou a klientom sa vyskytla chyba.\n psycopg2: {err}')
        exit()

