from os import getlogin
from msvcrt import getch
import random

import psycopg2
from psycopg2 import sql

from session.session import create_session

cursor, conn = create_session(SU=True)
conn.autocommit = False


def remove_database_record(affected_table: str, date_of_removal: str) -> int:
    query = sql.SQL('DELETE FROM {affected_table}\
    WHERE \"Path_ID\" IN(\
        SELECT \"ID\" FROM \"Path\" WHERE \"Path\" LIKE {date_of_removal}) RETURNING \"ID\";\
    ').format(affected_table = sql.Identifier(affected_table), date_of_removal=sql.Literal(f'{date_of_removal}%'))
    
    try:
        cursor.execute(query)
        return len(cursor.fetchall())
    except:
        conn.rollback()
        conn.close()
        exit()



def select_number_of_record_for_deletion(affected_table:str, date_of_removal:str) -> int:
    query = sql.SQL('SELECT COUNT({table}.{id}) FROM {table} INNER JOIN {path_table} ON {table}.{path_id} = {path_table}.{id}\
                    WHERE {path_table}.{path} LIKE {user_input}'
                    
                    )\
                    .format(table=sql.Identifier(affected_table), path_table=sql.Identifier('Path'), id = sql.Identifier('ID'),\
                             path_id = sql.Identifier('Path_ID'), path=sql.Identifier('Path'), user_input=sql.Literal(f'{date_of_removal}%'))
    
    try:
        cursor.execute(query)
        found_record_for_deletion = cursor.fetchall()[0][0]
        return found_record_for_deletion
    except Exception:
        print('Chyba 123: Nepodarilo sa verifikovať počet záznamov. Ukončujem aplikáciu.')
        conn.close()
        exit()
        



def get_table_name_for_deletion() -> str:
    match input('Ak chcete odstrániť konfiguračné záznamy KAM, zadajte KAM. Ak chcete odstrániť záznamy programového vybavenia PAP, zadajte PAP: ').lower():
        case 'kam':
            return 'Configuration'
        case 'pap':
            return 'Program'
        case _:
            print('Nesprávny vstup, zadajte ho znova.')
            get_table_name_for_deletion()


def user_initiated_record_removal():
    print('Chystáte sa odstrániť používateľské záznamy, chcete pokračovať? (Y/N)')
    user_input = getch().lower()
    if user_input != b'y':
        exit()

    date_of_removal = input('Zadajte rok a mesiac v ktorom chcete odstrániť záznamy. Napr. 2020/01 alebo 2025 alebo 2015/12: ')

    #Get table name
    affected_table = get_table_name_for_deletion()

    #Get number of records for deletion
    found_record_for_deletion = select_number_of_record_for_deletion(affected_table, date_of_removal)

    if found_record_for_deletion == 0:
        print('Neboli nájdené žiadne záznamy splňújúce podmienky na odstránenie. \nUkončujem aplikáciu.')
        exit()

    print(f'Chystáte sa odstrániť {found_record_for_deletion} záznamov.')
    if int(input(f'Pre pokračovanie zadajte počet záznamov, ktoré sa chystáte odstrániť: ')) != found_record_for_deletion:
        print('Chyba 125: Zadali ste nesprávny počet záznamov. Ukončujem aplikáciu.')
        conn.close()
        exit()

    deleted_records = remove_database_record(affected_table, date_of_removal)

    try:
        if found_record_for_deletion != deleted_records:
            conn.rollback()
        else:
            conn.commit()
            print(f'{found_record_for_deletion} záznamov bolo úspešne odstránených')
    except:
        pass

    conn.rollback()
    conn.close()