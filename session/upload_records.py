from datetime import datetime
import time
from sys import exit
import pickle
from os.path import abspath, dirname, join
import io


from psycopg2 import sql
import psycopg2

from session.session import create_session
import classes




def upload_unique_and_add_foreign_keys(absent_parameters: set,table_name: str,  cursor) -> None:
    # try:
        query = sql.SQL('SELECT MAX({id}) FROM {table_name};').format(id = sql.Identifier("ID"), table_name = sql.Identifier(table_name))
        cursor.execute(query)
        last_id = cursor.fetchone()[0] + 1

        absent_parameters = [x.replace('~', 'ASCII(126)') if x is not None and isinstance(x, str) else x for x in absent_parameters]
        data = '\n'.join('{}~{}'.format(last_id + i, x) for i, x in enumerate(absent_parameters))
        
        data_file = io.StringIO(data)
        if table_name == "Actor":
            cursor.copy_from(data_file, table_name, sep='~', columns=('ID', 'Actor_key'))
        else:
            cursor.copy_from(data_file, table_name, sep='~')


        return dict(zip(absent_parameters,range(last_id,last_id+len(absent_parameters)))) 
    # except:
    #     print("Chyba pri pridávaní chýbajúcich záznamov")
    #     return None




def download_data_as_dict(table:sql.Identifier, column:sql.Identifier, cursor) -> dict:
    query = sql.SQL('SELECT {ID}, {column} FROM {table};').format(column = column, ID = sql.Identifier("ID"), table = table)
    cursor.execute(query)
    response = cursor.fetchall()
    temp = {}
    for i, row in enumerate(response):
        temp[row[1]] = row[0] 
        
    return temp



parsing_start_time = time.perf_counter()
# def upload_records() -> None:
def upload_records(records:list, total_number_of_records:int, records_with_invalid_expression:int) -> None:


    #check if there are any records to be uploaded
    number_of_satisfying_records = len(records)
    if number_of_satisfying_records == 0: 
        print('Chyba 107: Žiaden zo záznamov sa nepodarilo spracovať, nič sa nanahrá.')
        exit() 
           
    #output stats   
    print("-"*80)
    with open('temp/processed_records.pickle', 'wb') as file:
        pickle.dump(records, file)
        print('Spracované zázamy sú zálohované. Cesta: {}\n'.format(abspath(join(dirname(__file__), '/temp/processed_records.pickle'))) )

    end_time = time.perf_counter()
    print("čas spracovania: {} sekúnd \n".format(end_time-parsing_start_time))
    print("Spracované záznamy: {} / {} ".format(number_of_satisfying_records ,total_number_of_records))
    print("Nespracované záznamy: {} z toho platných: {}".format(total_number_of_records-number_of_satisfying_records, total_number_of_records-number_of_satisfying_records-records_with_invalid_expression))
    print("Úspešnosť spracovania platných záznamov: {}%: ".format(100*number_of_satisfying_records/(total_number_of_records-records_with_invalid_expression)))

    #create DB session
    cursor, conn = create_session()

    conn.autocommit = False



    paths, existing_database_paths, actors, boards, HDV, software = {}, {}, {}, {}, {}, {}

    #fetch data from DB
    def fetch_database_data():
        try:

            nonlocal paths, existing_database_paths, actors, boards, HDV, software
            paths = download_data_as_dict(sql.Identifier("Path"), sql.Identifier("Path"), cursor)
            existing_database_paths = paths.copy()
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


    s = time.perf_counter()
    # Create new set object as difference of extracted parameters and parameters found in database

    absent_paths, absent_HDV, absent_actors, absent_boards, absent_software = [], [], [], [], [] 

    for x in records:

        absent_paths.append(x.get_path()) 
        absent_HDV.append(x.get_HDV())


        if isinstance(x, classes.log_classes.PAPRecordBuilder):
            absent_actors.append(x.get_actor())
            absent_boards.append(x.get_board())
            absent_software.append(x.get_software())

        elif isinstance(x, classes.log_classes.KAMRecordBuilder):
            # absent_actors.extend([x.get_M_actor(), x.get_C_actor()])
            absent_boards.extend([x.get_M_programmed_board(), x.get_C_programmed_board()])
            absent_software.extend([x.get_M_programmed_software(), x.get_C_programmed_software()])
        else:
            print('There has been a problem.')

    absent_paths = set(absent_paths) - set(paths.keys())
    absent_HDV = set(absent_HDV) - set(HDV.keys())
    absent_actors = set(absent_actors) - set(actors.keys())
    absent_boards = set(absent_boards) - set(boards.keys())
    absent_software = set(absent_software) - set(software.keys())

    e = time.perf_counter()

    # Print time taken to compute set difference for all parameters
    print(e-s)

    actors.update(upload_unique_and_add_foreign_keys(absent_actors, "Actor", cursor))
    paths.update(upload_unique_and_add_foreign_keys(absent_paths, "Path", cursor))
    boards.update(upload_unique_and_add_foreign_keys(absent_boards, "Board", cursor))
    HDV.update(upload_unique_and_add_foreign_keys(absent_HDV, "HDV", cursor))
    software.update(upload_unique_and_add_foreign_keys(absent_HDV, "Software", cursor))


    
    
    conn.rollback()
    # conn.commit()

    #upload records

    # parsed_values will store content alongside to foreign key references for each record
    upload_PAP_string = ''
    upload_KAM_string = ''

    for i,recordX in enumerate(records):
        record = {}
        # if record['Path'] in existing_database_paths:
        #     print(f'Nájdený záznam s duplicitnou cestou k súboru: {record["Path"]} prerušujem nahrávanie, spracované súbory sú uložené')
        #     exit()

        record["Path"] = paths[recordX.get_path()]

        record["Actor"] = paths[recordX.get_actor()]

        record["Board"] = upload_unique_and_add_foreign_keys(cursor,record["Board"],boards,"Board",["id", "Board_version"])

        if record["HDV"] == None:
            record["HDV"] = "None"

        record["HDV"] = upload_unique_and_add_foreign_keys(cursor,record["HDV"],HDV,"HDV",["id", "HDV"])

        record["Software"] = upload_unique_and_add_foreign_keys(cursor,record["Software"],software,"Software",["id", "Version"])

        parsed_values+="({HDV},\'{PAP_date}\', {actor}, {board}, {software}, \'{compilation_datetime}\', {active}, {path}, \'{CHSUM_Flash}\', \'{CHSUM_EEPROM}\' ,\'{time_now}\'),".format(HDV = record["HDV"], PAP_date=record["PAP_date"], actor=record["Actor"], board=record["Board"], software=record["Software"], compilation_datetime=record["Compilation_datetime"], active="True", path=record["Path"], CHSUM_Flash=record["Checksum_Flash"] , CHSUM_EEPROM=record["Checksum_EEPROM"],time_now=datetime.now())

        if (i+1)%100==0:
            #remove last comma from parsed_values 
            parsed_values=parsed_values[:-1]
            cursor.execute("INSERT INTO \"Program\"(\"HDV\",\"PAP_date\",\"Actor\",\"Board\",\"Software\",\"Compilation_datetime\",\"Active\",\"Path\", \"CHSUM_Flash\", \"CHSUM_EEPROM\", \"Log_processed_datetime\"){}".format(parsed_values))
            conn.commit()
            parsed_values="VALUES"
            print("Záznamy {} - {} boli nahrané do databázy".format(i-99,i+1))


    parsed_values=parsed_values[:-1]
    cursor.execute("INSERT INTO \"Program\"(\"HDV\",\"PAP_date\",\"Actor\",\"Board\",\"Software\",\"Compilation_datetime\",\"Active\",\"Path\", \"CHSUM_Flash\", \"CHSUM_EEPROM\", \"Log_processed_datetime\"){}".format(parsed_values))
    print("Záznamy nahraté do databázy")
    conn.commit()

    cursor.close()
    conn.close()

    exit()    