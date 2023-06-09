from datetime import datetime
from time import strftime, perf_counter
import time
from sys import exit
import pickle
from os.path import abspath, dirname, join
import os
import io


from psycopg2 import sql
import psycopg2

from session.session import create_session
import classes






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
    except:
        print("Chyba 119: Pri pridávaní parmetrov do databáze nastala chyba.")
        return None





# This module downloads all parameters with their respective IDs
def download_data_as_dict(table:sql.Identifier, column:sql.Identifier, cursor) -> dict:
    query = sql.SQL('SELECT {ID}, {column} FROM {table};').format(column = column, ID = sql.Identifier("ID"), table = table)
    cursor.execute(query)
    response = cursor.fetchall()
    temp = {}
    for i, row in enumerate(response):
        temp[row[1]] = row[0] 
        
    return temp






parsing_start_time = time.perf_counter()
def upload_records(records:list, total_number_of_records:int, records_with_invalid_expression:int) -> None:
    #check if there are any records to be uploaded
    number_of_satisfying_records = len(records)
    if number_of_satisfying_records == 0: 
        print('Chyba 107: Žiaden zo záznamov sa nepodarilo spracovať, nič sa nanahrá.')
        exit() 
           
    #output stats   
    print("-"*80)


    try:
        stats = {'total_number_of_records' : total_number_of_records, 'records_with_invalid_expression' : records_with_invalid_expression}
        with open(abspath(join(dirname(__file__), '../temp/stats.pickle')), 'wb') as file:
            pickle.dump(stats, file)
        with open(abspath(join(dirname(__file__), '../temp/LPTB.pickle')), 'wb') as file:
            pickle.dump(records, file)
            print('Spracované zázamy sú zálohované. Cesta: {}\n'.format(abspath(join(dirname(__file__), '../temp/processed_records.pickle'))))
    except:
        print("Chyba 120: Spracované súbory nebolo možné zálohovať. Uistite sa, že má program dostatočné povolenia pre vytváranie súborov.")



    end_time = time.perf_counter()
    print('-'*80)
    print("čas spracovania: {} sekúnd \n".format(end_time-parsing_start_time))
    print("Spracované záznamy: {} / {} ".format(number_of_satisfying_records ,total_number_of_records))
    print("Nespracované záznamy: {} z toho platných: {}".format(total_number_of_records-number_of_satisfying_records, total_number_of_records-number_of_satisfying_records-records_with_invalid_expression))
    print("Úspešnosť spracovania platných záznamov: {}%:".format(100*number_of_satisfying_records/(total_number_of_records-records_with_invalid_expression)))
    print('-'*80)
    print("Inicializácia relácie s databázou")
    #create DB session
    cursor, conn = create_session()
    conn.autocommit = False
    print("Inicializácia relácie s databázou: úspech")
    print('-'*80)

    print('-'*80)
    print("Sťahovanie parametrov z databázy")
    paths, previous_database_paths, actors, boards, HDV, software = {}, {}, {}, {}, {}, {}
    #fetch data from DB
    def fetch_database_data():
        try:
            nonlocal paths, previous_database_paths, actors, boards, HDV, software
            paths = download_data_as_dict(sql.Identifier("Path"), sql.Identifier("Path"), cursor)
            previous_database_paths = paths.copy()
            actors = download_data_as_dict(sql.Identifier("Actor"), sql.Identifier("Actor_key"), cursor)
            boards = download_data_as_dict(sql.Identifier("Board"), sql.Identifier("Board_version"), cursor)
            HDV = download_data_as_dict(sql.Identifier("HDV"), sql.Identifier("HDV"), cursor)
            software = download_data_as_dict(sql.Identifier("Software"), sql.Identifier("Version"), cursor)
        except:
            print('Chyba 110: Nastala chyba pri sťahovaní dát. \nChcete sa o to pokúsiť znova? (Y/N)')
            if input().lower() == "y":
                fetch_database_data()
            else:
                cursor.close()
                conn.close()
                exit()

    fetch_database_data()

    
    print("Sťahovanie parametrov z databázy: úspech")
    print('-'*80)

    print('-'*80)
    print("Vyhľadávanie chýbajúcich parametrov a nahrávananie do databázy")
    

    # Create new set object as difference of extracted parameters and parameters found in database
    absent_paths, absent_HDV, absent_actors, absent_boards, absent_software = [], [], [], [], [] 
    for record_object in records:

        absent_paths.append(record_object.get_path()) 
        absent_HDV.append(record_object.get_HDV())

        if isinstance(record_object, classes.log_classes.PAPRecordBuilder):
            absent_actors.append(record_object.get_actor())
            absent_boards.append(record_object.get_board())
            absent_software.append(record_object.get_software())

        elif isinstance(record_object, classes.log_classes.KAMRecordBuilder):
            # absent_actors.extend([record_object.get_M_actor(), record_object.get_C_actor()])
            absent_boards.extend([record_object.get_M_programmed_board(), record_object.get_C_programmed_board()])
            absent_software.extend([record_object.get_M_programmed_software(), record_object.get_C_programmed_software()])
        else:
            print('Chyba 121: V procese kopírovania obsahu záznamových objektov do poľa došlu ku chybe')



    #Compute set difference between uploaded and local data (parameters)
    absent_paths = set(absent_paths) - set(paths.keys())
    absent_HDV = set(absent_HDV) - set(HDV.keys())
    absent_actors = set(absent_actors) - set(actors.keys())
    absent_boards = set(absent_boards) - set(boards.keys())
    absent_software = set(absent_software) - set(software.keys())


    #Upload the above found sets and associate them with IDs. Return dictionary containing IDs and parameters. 
    #Update existing local parameters to represent new database status

    try:
        actors.update(upload_unique_and_add_foreign_keys(absent_actors, "Actor", cursor, "Actor_key"))
        paths.update(upload_unique_and_add_foreign_keys(absent_paths, "Path", cursor, "Path"))
        boards.update(upload_unique_and_add_foreign_keys(absent_boards, "Board", cursor, "Board_version"))
        HDV.update(upload_unique_and_add_foreign_keys(absent_HDV, "HDV", cursor, "HDV"))
        software.update(upload_unique_and_add_foreign_keys(absent_software, "Software", cursor, "Version"))
        conn.commit()    
    except:
        conn.rollback()
        print('Chyba 119: Ukončujem program')
        exit()

    print("Vyhľadávanie chýbajúcich parametrov a nahrávananie do databázy: úspech")
    print('-'*80)


    print("Nahrávanie záznamov do databázy")
    # parsed_values will store content alongside foreign key references for each record
    upload_PAP_string = ''
    upload_KAM_string = ''

    sclek=perf_counter()

    uploaded_records_counter = 0
    for record_object in records:

        record = {}
        if record_object.get_path() in previous_database_paths:
            print(f'Nájdený záznam s duplicitnou cestou k súboru: {record_object.get_path()} prerušujem nahrávanie.\nUkončujem program')
            exit()

        record["Path"] = paths[record_object.get_path()]
        record["HDV"] = HDV[record_object.get_HDV()]



        if isinstance(record_object, classes.log_classes.PAPRecordBuilder):
            if record_object.get_compilation_date() is not None:
                record["Compilation_date"] = record_object.get_compilation_date().strftime(r'%Y-%m-%d')
            else:
                record["Compilation_date"] = 'None'

            record["Datetime"] = record_object.get_datetime().strftime(r'%Y-%m-%d %H:%M:%S') 
            record["Processed_datetime"] = datetime.now().strftime(r'%Y-%m-%d %H:%M:%S') 
            record["Actor"] = actors[record_object.get_actor()]
            record["Board"] = boards[record_object.get_board()]
            record["Software"] = software[record_object.get_software()]
            record["checksum_Flash"] = record_object.get_checksum_Flash()
            record["checksum_EEPROM"] = record_object.get_checksum_EEPROM()
            upload_PAP_string = ''.join([upload_PAP_string, f'{record["HDV"]}~{record["Datetime"]}~{record["Compilation_date"]}~{record["Actor"]}~{record["Board"]}~{record["checksum_Flash"]}~{record["checksum_EEPROM"]}\
                ~{record["Software"]}~True~{record["Path"]}~{record["Processed_datetime"]}', '\n'])

        elif isinstance(record_object, classes.log_classes.KAMRecordBuilder):  
            record["config_datetime"] = record_object.get_config_datetime().strftime(r'%Y-%m-%d %H:%M:%S') 
            
            # Channel M
            record["M_programmed_date"] = record_object.get_M_programmed_date().strftime(r'%Y-%m-%d') 
            # record["M_config_actor"] = actors[record_object.get_M_programmed_actor()]
            record["M_software_ID"] = software[record_object.get_M_programmed_software()]
            record["M_board_ID"] = boards[record_object.get_M_programmed_board()]
            record["M_functonality"] = record_object.get_M_functionality()
            record["M_configuation"] = record_object.get_M_configuration()
            record["M_IRC"] = record_object.get_M_IRC()
            record["M_spare_part"] = record_object.get_M_spare_part()

            # Channel C

            if record_object.get_multichannel():
                record["C_programmed_date"] = record_object.get_C_programmed_date().strftime(r'%Y-%m-%d') 
                # record["C_config_actor"] = actors[record_object.get_C_programmed_actor()]
                record["C_software_ID"] = software[record_object.get_C_programmed_software()]
                record["C_board_ID"] = boards[record_object.get_C_programmed_board()]
                record["C_functonality"] = record_object.get_C_functionality()
                record["C_configuation"] = record_object.get_C_configuration()
                record["C_IRC"] = record_object.get_C_IRC()
                record["C_spare_part"] = record_object.get_C_spare_part()
            else:
                record["C_programmed_date"], record["C_software_ID"], record["C_board_ID"], record["C_functonality"], record["C_configuation"], record["C_IRC"], record["C_spare_part"] = '1000-01-01 00:00:00', None, None, None, None, 0, 0
            
            upload_KAM_string = ''.join([upload_KAM_string, f'{record["HDV"]}~{record["config_datetime"]}~{record["M_programmed_date"]}~{record["M_software_ID"]}~{record["M_board_ID"]}~{record["M_functonality"]}~{record["M_configuation"]}\
                ~{record["M_IRC"]}~{record["M_spare_part"]}~{record["C_programmed_date"]}~{record["C_software_ID"]}~{record["C_board_ID"]}~{record["C_functonality"]}~{record["C_configuation"]}~{record["C_IRC"]}\
                ~{record["C_spare_part"]}~True~{record["Path"]}', '\n'])


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
        cursor.copy_from(upload_PAP_file, "Program", sep='~', null='None', columns=('HDV_ID', 'PAP_datetime', 'Compilation_date', 'Actor_ID', 'Board_ID', 'Checksum_Flash', 'Checksum_EEPROM', 'Software_ID', 'Active', 'Path_ID', 'Processed_datetime'))
        cursor.copy_from(upload_KAM_file, "Configuration", sep='~', null='None', columns=('HDV_ID', 'Config_datetime', 'M_programmed_date', 'M_software_ID', 'M_board_ID', 'M_functionality', 'M_configuration', 'M_IRC', 'M_spare_part', 'C_programmed_date', 'C_software_ID', 'C_board_ID', 'C_functionality', 'C_configuration', 'C_IRC', 'C_spare_part', 'Active', 'Path_ID'))
        conn.commit()
    except:
        conn.rollback()
        print('Chyba 118: Zlyhanie kopírovania súboru (inštancie StringIO) do databázy. Ukončujem program.')
        return None
    
    print("Nahrávanie záznamov do databázy: úspech")
    print('-'*80)
    print(perf_counter()-sclek)

    print(f"\nDo databázy bolo nahraných {uploaded_records_counter} súborov., čo tvorí {uploaded_records_counter/number_of_satisfying_records*100}% spracovaných záznamov")
    print('Ukončujem reláciu')
    cursor.close()
    conn.close()

    print('Relácia ukončená. Stlačte ENTER pre ukončenie programu')
    input()

    return None    




def recover_files() -> None:
        stats_path = abspath(join(dirname(__file__), '../temp/stats.pickle'))
        record_path = abspath(join(dirname(__file__), '../temp/LPTB.pickle'))

        if not os.path.isfile(stats_path) or not os.path.isfile(record_path):
            print(f'Chyba 121: Záloha neexistuje. Hľadaná cesta: {stats_path}, {record_path}.\nUkončujem program')
            exit()

        try:
            with open(stats_path, 'rb') as file:
                stats = pickle.load(file)

            with open(record_path, 'rb') as file:
                records = pickle.load(file)
        except:
            print("Chyba 101: Program nemá povolenia na čítanie zálohy.\nUkončujem program")
            exit()
            
        upload_records(records, stats['total_number_of_records'], stats['records_with_invalid_expression'])
        
        