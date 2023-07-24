from datetime import datetime
from time import strftime, perf_counter
import time
from sys import exit
import pickle
from os.path import abspath, dirname, join, exists
from os import path, access, R_OK, W_OK, getcwd
import io
from msvcrt import getch


from psycopg2 import sql
import psycopg2

from session.session import create_session
import classes


CWD = getcwd()

failure_notation = {
    'PAP_timestamp': 'Časová známka PAP - REGEX',
    'PAP_SW': 'Verzia SW - REGEX',
    'PAP_SW_detection': 'Verzia SW - overenie',
    'PAP_safebytes': 'Safebytes - REGEX',
    'safebytes_version_encoding': 'Verzia safebytes',
    'PAP_regex_sw_doesnt_match': 'Nesúlad SW REGEX a Safebytes',
    'PAP_programmed_date_1': 'Chyb. substitút za dátum PAP',
    'PAP_programmed_date_2': 'Dátum programovania PAP 2',
    'KAM_config_date': 'Časová známka KAM - REGEX',
    'KAM_actor_M': 'KAM Actor programovania SW kanálu M - REGEX',
    'KAM_actor_C': 'KAM Actor programovania SW kanálu C - REGEX',
    'KAM_HDV': 'KAM HDV - REGEX',
    'KAM_configuration_M': 'KAM Konfigurácia kanál M - REGEX',
    'KAM_configuration_C': 'KAM Konfigurácia kanál C - REGEX',
    'KAM_SW_M': 'SW kanál M - REGEX',
    'KAM_SW_C': 'KAM SW kanál C - REGEX',
    'KAM_prog_actor_M': 'KAM Actor kanálu M  programovanie - REGEX',
    'KAM_prog_actor_C': 'KAM Actor kanálu C programovanie - REGEX',
    'KAM_board_M': 'KAM kanál M VNUM - REGEX',
    'KAM_board_C': 'KAM kanál C VNUM - REGEX',
    'KAM_programmed_date_M': 'KAM kanál M Časová známka',
    'KAM_programmed_date_C': 'KAM kanál C Časová známka',
    'KAM_configured_device_M': 'KAM kanál M Konfigurované zariadenie',
    'KAM_configured_device_C': 'KAM kanál C Konfigurované zariadenie',
    'noname_SW': 'KAM Softvér je nastavený ako \'noname\''
}


# Check if file exists, is accessible and can be opened
def verify_file_OK(relative_path, file_description, mode):
    file_path = join(CWD,relative_path)
    if not exists(file_path):
        print(f'Chyba 100: Súbor {file_description} nebol nájdený. Cesta: {file_path}')
        return False

    if mode == 'rb':
        if not access(file_path, R_OK):
            print(f'Chyba 101: Na čítanie {file_description} nemáte dostatčné oprávnenia. Cesta: {file_path}')
            return False
        
    elif mode == 'wb':
        if not access(file_path, W_OK):
            print(f'Chyba 101: Na zápis {file_description} nemáte dostatčné oprávnenia. Cesta: {file_path}')
            return False
    return True




# This module uploads missing found parameters to database and returns their IDs
def upload_unique_and_add_foreign_keys(absent_parameters: set,table_name: str, cursor, selected_column:str) -> None:
    try:
        query = sql.SQL('SELECT MAX({id}) FROM {table_name};').format(id = sql.Identifier('ID'), table_name = sql.Identifier(table_name))
        cursor.execute(query)
        last_id = cursor.fetchone()[0]
        if last_id is None:
            last_id = 1
        else:
            last_id+= 1

        absent_parameters = [x.replace('~', 'ASCII(126)') if x is not None and isinstance(x, str) else x for x in absent_parameters]
        data = '\n'.join('{}~{}'.format(last_id + i, x) for i, x in enumerate(absent_parameters))
        
        data_file = io.StringIO(data)

        cursor.copy_from(data_file, table_name, sep='~', null='None', columns=('ID', selected_column))
        return dict(zip(absent_parameters,range(last_id,last_id+len(absent_parameters)))) 
    except Exception as err:
        print(f'Chyba 119: Pri pridávaní parmetrov do databázy nastala chyba.\n psycopg2: {err}')
        return None





# This module downloads all parameters with their respective IDs
def download_data_as_dict(table:sql.Identifier, column:sql.Identifier, cursor) -> dict:
    query = sql.SQL('SELECT {ID}, {column} FROM {table};').format(column = column, ID = sql.Identifier('ID'), table = table)
    cursor.execute(query)
    response = cursor.fetchall()
    temp = {}
    for i, row in enumerate(response):
        temp[row[1]] = row[0] 
        
    return temp



#fetch data from DB
def fetch_database_data(paths, previous_database_paths, boards, HDV, software, conn, cursor):
    try:
        paths = download_data_as_dict(sql.Identifier('Path'), sql.Identifier('Path'), cursor)
        previous_database_paths = paths.copy()
        boards = download_data_as_dict(sql.Identifier('Board'), sql.Identifier('Board_version'), cursor)
        HDV = download_data_as_dict(sql.Identifier('HDV'), sql.Identifier('HDV'), cursor)
        software = download_data_as_dict(sql.Identifier('Software'), sql.Identifier('Version'), cursor)
        return paths, previous_database_paths, boards, HDV, software
    except Exception as err:
        print(f'Chyba 110: Nastala chyba pri sťahovaní dát. \npsycopg2: {err}\nChcete sa o to pokúsiť znova? (Y/N)')
        if getch().lower() == b'y':
            conn.rollback()
            return fetch_database_data(paths, previous_database_paths, boards, HDV, software, conn, cursor)
        else:
            cursor.close()
            conn.close()
            return None





parsing_start_time = time.perf_counter()
def upload_records(records:list, total_number_of_records:int, records_with_invalid_expression:int, failures: dict) -> None:
    #check if there are any records to be uploaded
    number_of_satisfying_records = len(records)
    if number_of_satisfying_records == 0: 
        print('Chyba 107: Žiaden zo záznamov sa nepodarilo spracovať, nič sa nanahrá.')
        return None 
           
    #output stats   
    print('-'*80)


    try:
        stats = {'total_number_of_records' : total_number_of_records, 'records_with_invalid_expression' : records_with_invalid_expression, 'failures' : failures}
        
        
        if not verify_file_OK('temp/stats.pickle', 'štatistiky spracovania', 'wb'):
            raise Exception
 
        with open(join(CWD, 'temp/stats.pickle'), 'wb') as file:
            pickle.dump(stats, file)

        if not verify_file_OK('temp/stats.pickle', 'obsahu spracovania', 'wb'):
            raise Exception
        with open(join(CWD, 'temp/LPTB.pickle'), 'wb') as file:
            pickle.dump(records, file)
            print('Spracované zázamy sú zálohované. Cesta: {}\n'.format(join(CWD, 'temp/')))

    except Exception as err:
        print(f'Chyba 120: Spracované súbory nebolo možné zálohovať. Uistite sa, že má program dostatočné povolenia pre vytváranie súborov.Err_desc:{err}')



    end_time = time.perf_counter()
    print('-'*80)
    print('čas spracovania: {} sekúnd \n'.format(end_time-parsing_start_time))
    print('Spracované záznamy: {} / {} '.format(number_of_satisfying_records ,total_number_of_records))
    print('Nespracované záznamy: {} z toho platných: {}'.format(total_number_of_records-number_of_satisfying_records, total_number_of_records-number_of_satisfying_records-records_with_invalid_expression))
    print('Úspešnosť spracovania platných záznamov: {}%:'.format(100*number_of_satisfying_records/(total_number_of_records-records_with_invalid_expression)))

    print('Chcete vypísať štatistiku spracovania (Y/N)')
    if getch().lower() == b'y':
        failed_total = sum(failures[x] for x in failures)
        failures = sorted(failures.items(),key = lambda item: item[1]  ,  reverse=True)
        for failure in failures:
            if failure[1] == 0:
                continue
            print(f'{failure_notation[failure[0]]} : {failure[1]} : {round(100*failure[1]/failed_total,2)}% zo zlyhaných')


    print('-'*80)
    print('Inicializácia relácie s databázou')
    #create DB session
    cursor, conn = create_session()
    print('Inicializácia relácie s databázou: úspech')
    print('-'*80)

    print('-'*80)
    print('Sťahovanie parametrov z databázy')
    
    paths, previous_database_paths, boards, HDV, software = {}, {}, {}, {}, {}

    temp = fetch_database_data(paths, previous_database_paths, boards, HDV, software, conn, cursor)

    if temp is None:
        return None
    else:
        paths, previous_database_paths, boards, HDV, software = temp

    
    print('Sťahovanie parametrov z databázy: úspech')
    print('-'*80)

    print('-'*80)
    print('Vyhľadávanie chýbajúcich parametrov a nahrávananie do databázy')
    
    # Create new set object as difference of extracted parameters and parameters found in database
    absent_paths, absent_HDV, absent_boards, absent_software = [], [], [], []
    for record_object in records:

        absent_paths.append(record_object.get_path()) 
        absent_HDV.append(record_object.get_HDV())

        if isinstance(record_object, classes.log_classes.PAPRecordBuilder):
            absent_boards.append(record_object.get_board())
            absent_software.append(record_object.get_software())

        elif isinstance(record_object, classes.log_classes.KAMRecordBuilder):
            absent_boards.extend([record_object.get_M_programmed_board(), record_object.get_C_programmed_board()])
            absent_software.extend([record_object.get_M_programmed_software(), record_object.get_C_programmed_software()])
        else:
            print('Chyba 121: V procese kopírovania obsahu záznamových objektov do poľa došlu ku chybe')



    #Compute set difference between uploaded and local data (parameters)
    absent_paths = set(absent_paths) - set(paths.keys())
    absent_HDV = set(absent_HDV) - set(HDV.keys())
    absent_boards = set(absent_boards) - set(boards.keys())
    absent_software = set(absent_software) - set(software.keys())


    #Upload the above found sets and associate them with IDs. Return dictionary containing IDs and parameters. 
    #Update existing local parameters to represent new database status

    try:
        paths.update(upload_unique_and_add_foreign_keys(absent_paths, 'Path', cursor, 'Path'))
        boards.update(upload_unique_and_add_foreign_keys(absent_boards, 'Board', cursor, 'Board_version'))
        HDV.update(upload_unique_and_add_foreign_keys(absent_HDV, 'HDV', cursor, 'HDV'))
        software.update(upload_unique_and_add_foreign_keys(absent_software, 'Software', cursor, 'Version')) 
    except Exception as err:
        conn.rollback()
        print(f'Chyba 119: Pri aktualizacií parametrov databázy nastala chyba. \n Psycopg2: {err}\n Návrat do menu.')
        return None

    print('Vyhľadávanie chýbajúcich parametrov a nahrávananie do databázy: úspech')
    print('-'*80)


    print('Nahrávanie záznamov do databázy')
    # parsed_values will store content alongside foreign key references for each record
    upload_PAP_string = ''
    upload_KAM_string = ''

    sclek = perf_counter()

    uploaded_records_counter = 0

    for record_object in records:

        record = {}
        if record_object.get_path() in previous_database_paths:
            print(f'Nájdený záznam s duplicitnou cestou k súboru: {record_object.get_path()} prerušujem nahrávanie.\nNávrat do menu.')
            return None

        # General parameters
        record['Path'] = paths[record_object.get_path()]
        record['HDV'] = HDV[record_object.get_HDV()]


        #PAP record parameters
        if isinstance(record_object, classes.log_classes.PAPRecordBuilder):
            if record_object.get_compilation_date() is not None:
                record['Compilation_date'] = record_object.get_compilation_date().strftime(r'%Y-%m-%d')
            else:
                record['Compilation_date'] = 'None'

            record['Datetime'] = record_object.get_datetime().strftime(r'%Y-%m-%d %H:%M:%S') 
            record['Processed_datetime'] = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S') 
            record['Actor'] = record_object.get_actor()
            record['Board'] = boards[record_object.get_board()]
            record['Software'] = software[record_object.get_software()]
            record['checksum_Flash'] = record_object.get_checksum_Flash()
            record['checksum_EEPROM'] = record_object.get_checksum_EEPROM()
            upload_PAP_string = ''.join([upload_PAP_string, f"{record['HDV']}~{record['Datetime']}~{record['Compilation_date']}~{record['Actor']}~{record['Board']}~{record['checksum_Flash']}~{record['checksum_EEPROM']}\
                ~{record['Software']}~True~{record['Path']}~{record['Processed_datetime']}", '\n'])



        #KAM record parameters

        # Channel M parameters
        elif isinstance(record_object, classes.log_classes.KAMRecordBuilder):  
            record['M_configured_device'] = record_object.get_M_configured_device()
            record['config_datetime'] = record_object.get_config_datetime().strftime(r'%Y-%m-%d %H:%M:%S') 
            record['Processed_datetime'] = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S') 
            record['M_programmed_date'] = record_object.get_M_programmed_date().strftime(r'%Y-%m-%d') 
            # record['M_config_actor'] = actors[record_object.get_M_programmed_actor()]
            record['M_software_ID'] = software[record_object.get_M_programmed_software()]
            record['M_board_ID'] = boards[record_object.get_M_programmed_board()]
            record['M_functonality'] = record_object.get_M_functionality()
            record['M_configuation'] = record_object.get_M_configuration()
            record['M_IRC'] = record_object.get_M_IRC()
            record['M_spare_part'] = record_object.get_M_spare_part()

            # Channel C parameters
            if record_object.get_multichannel():
                record['C_configured_device'] = record_object.get_C_configured_device()
                record['C_programmed_date'] = record_object.get_C_programmed_date().strftime(r'%Y-%m-%d') 
                record['Processed_datetime'] = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S') 
                # record['C_config_actor'] = actors[record_object.get_C_programmed_actor()]
                record['C_software_ID'] = software[record_object.get_C_programmed_software()]
                record['C_board_ID'] = boards[record_object.get_C_programmed_board()]
                record['C_functonality'] = record_object.get_C_functionality()
                record['C_configuation'] = record_object.get_C_configuration()
                record['C_IRC'] = record_object.get_C_IRC()
                record['C_spare_part'] = record_object.get_C_spare_part()
            else:
                record['C_programmed_date'], record['C_software_ID'], record['C_board_ID'], record['C_functonality'], record['C_configuation'], record['C_configured_device'], record['C_IRC'], record['C_spare_part'] = None, None, None, None, None, None, 0, 0
            
            upload_KAM_string = ''.join([upload_KAM_string, f"{record['HDV']}~{record['config_datetime']}~{record['M_programmed_date']}~{record['M_software_ID']}~{record['M_board_ID']}~{record['M_functonality']}~{record['M_configuation']}\
                ~{record['M_IRC']}~{record['M_spare_part']}~{record['C_programmed_date']}~{record['C_software_ID']}~{record['C_board_ID']}~{record['C_functonality']}~{record['C_configuation']}~{record['C_IRC']}\
                ~{record['C_spare_part']}~True~{record['Path']}~{record['Processed_datetime']}~{record['M_configured_device']}~{record['C_configured_device']}", '\n'])


        else:
            continue
        uploaded_records_counter += 1

    try:
        upload_PAP_file = io.StringIO(upload_PAP_string)
        upload_KAM_file = io.StringIO(upload_KAM_string)
    except:
        print('Chyba 117: Zlyhanie konverzie reťazca na StringIO. Ukončujem nahrávanie')
        return None
    

    try:
        cursor.copy_from(upload_PAP_file, 'Program', sep='~', null='None', columns=('HDV_ID', 'PAP_datetime', 'Compilation_date', 'Actor_SharePointID', 'Board_ID', 'Checksum_Flash', 'Checksum_EEPROM', 'Software_ID', 'Active', 'Path_ID', 'Processed_datetime'))
        cursor.copy_from(upload_KAM_file, 'Configuration', sep='~', null='None', columns=('HDV_ID', 'Config_datetime', 'M_programmed_date', 'M_software_ID', 'M_board_ID', 'M_functionality', 'M_configuration', 'M_IRC', 'M_spare_part','C_programmed_date', 'C_software_ID', 'C_board_ID', 'C_functionality', 'C_configuration', 'C_IRC', 'C_spare_part', 'Active', 'Path_ID', 'Processed_datetime','M_configured_device','C_configured_device'))
        conn.commit()
    except Exception as err:
        conn.rollback()
        print(f'Chyba 118: Zlyhanie kopírovania záznamov (reťazca ako inštancia StringIO) do databázy. Ukončujem program. \n psycopg2: {err}')
        return None
    
    print('Nahrávanie záznamov do databázy: úspech')
    print('-'*80)
    print(f'Čas spracovania: {perf_counter()-sclek}s')

    print(f'\nDo databázy bolo nahraných {uploaded_records_counter} súborov., čo tvorí {uploaded_records_counter/number_of_satisfying_records*100}% spracovaných záznamov')
    print('Ukončujem reláciu.')
    cursor.close()
    conn.close()


    return None    




def recover_files() -> None:
        stats_path = join(CWD, 'temp/stats.pickle')
        record_path = join(CWD, 'temp/LPTB.pickle')

        if not path.isfile(stats_path) or not path.isfile(record_path):
            print(f'Chyba 121: Záloha neexistuje. Hľadaná cesta: {stats_path} a {record_path}.')
            return None

        try:

            if not verify_file_OK(stats_path, 'štatistiky spracovania', 'rb'):
                Exception

            with open(stats_path, 'rb') as file:
                stats = pickle.load(file)


            if not verify_file_OK(record_path, 'obsahu spracovania', 'rb'):
                Exception
            with open(record_path, 'rb') as file:
                records = pickle.load(file)
        except:
            print('Chyba 101: Program nemá povolenia na čítanie zálohy.\nUkončujem program')
            return None
            
        upload_records(records, stats['total_number_of_records'], stats['records_with_invalid_expression'], stats['failures'])
        
        