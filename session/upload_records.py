from Database.Session import create_session
from datetime import datetime
import time
from sys import exit


#check if 
def upload_unique_and_add_foreign_keys(cursor,dict_parameter,database_parameters,table_name,column_names) -> None:
    if dict_parameter not in database_parameters:
        cursor.execute("SELECT MAX(\"id\") FROM \"{table_name}\";".format(table_name = table_name))
        id=cursor.fetchone()[0]+1
        cursor.execute("INSERT INTO \"{table_name}\" (\"{column_names[0]}\", \"{column_names[1]}\") VALUES({id}, \'{dict_parameter}\')".format(table_name = table_name, column_names = column_names, id = id, dict_parameter = dict_parameter))
        database_parameters[dict_parameter]=id
        return id
    else:
        return database_parameters[dict_parameter]








parsing_start_time = time.perf_counter()
def upload_records(satisfying_records:list, total_number_of_records:int):

    #check if there are any records to upload
    if len(satisfying_records) == 0: 
        print('Chyba 107: Žiaden zo záznamov sa nepodarilo spracovať, nič sa nanahrá.')
        exit()     
        
    #output stats   
    end_time = time.perf_counter()
    print("-------------------------")
    print("čas spracovania: {}\n".format(end_time-parsing_start_time))
    print("Spracované záznamy: {} / {} \n".format(len(satisfying_records) ,total_number_of_records))
    print("Nespracované záznamy: {} \n".format(total_number_of_records-len(satisfying_records)))


    #create DB session
    cursor, conn = create_session()

    #fetch data from DB
    try:
        cursor.execute("SELECT \"Path\" FROM \"Path\";")
        query_resp=cursor.fetchall()
        paths={}
        for i,path in enumerate(query_resp):
            paths[path[0]]=i+1
        existing_database_paths=paths.copy()


        cursor.execute("SELECT \"Actor_key\" FROM \"Actor\";")
        query_resp=cursor.fetchall()
        actors={}
        for i,actor in enumerate(query_resp):
            actors[actor[0]]=i+1

        cursor.execute("SELECT \"Board_version\" FROM \"Board\";")
        query_resp=cursor.fetchall()
        boards={}
        for i,board in enumerate(query_resp):
            boards[board[0]]=i+1

        cursor.execute("SELECT \"HDV\" FROM \"HDV\";")
        query_resp=cursor.fetchall()
        HDV={}
        for i,_ in enumerate(query_resp):
            HDV[_[0]]=i+1

        cursor.execute("SELECT \"Version\" FROM \"Software\";")
        query_resp=cursor.fetchall()
        software={}
        for i,_ in enumerate(query_resp):
            software[_[0]]=i+1

    except:
        print('Chyba 110: Nastala chyba pri sťahovaní dát. Skontrolujte pripojenie k databáze.')
        cursor.close()
        conn.close()
        exit()  

    #upload records
    records_dictionary=[]
    start_time=time.perf_counter()
    for i in range(len(satisfying_records)):
        records_dictionary.append(satisfying_records[i].PAP_to_dict())

    end_time=time.perf_counter()
    print('obj -> dict time: {} \n'.format(end_time-start_time))

    # parsed_values will store content alongside to foreign key references for each record
    parsed_values="VALUES"

    for i,record in enumerate(records_dictionary):
        if record["Path"] in existing_database_paths:
            print("Duplicitný záznam, spracované záznamy sa neuložia, ukončujem program")
            exit()

        record["Path"] = upload_unique_and_add_foreign_keys(cursor,record["Path"],paths,"Path",["id", "Path"])

        record["Actor"] = upload_unique_and_add_foreign_keys(cursor,record["Actor"],actors,"Actor",["id", "Actor_key"])

        record["Board"] = upload_unique_and_add_foreign_keys(cursor,record["Board"],boards,"Board",["id", "Board_version"])

        if record["HDV"] == None:
            record["HDV"] = "None"

        record["HDV"] = upload_unique_and_add_foreign_keys(cursor,record["HDV"],HDV,"HDV",["id", "HDV"])

        record["Software"] = upload_unique_and_add_foreign_keys(cursor,record["Software"],software,"Software",["id", "Version"])

        parsed_values+="({HDV},\'{PAP_date}\', {actor}, {board}, {software}, \'{compilation_timedate}\', {active}, {path}, \'{CHSUM_Flash}\', \'{CHSUM_EEPROM}\' ,\'{time_now}\'),".format(HDV = record["HDV"], PAP_date=record["PAP_date"], actor=record["Actor"], board=record["Board"], software=record["Software"], compilation_timedate=record["Compilation_timedate"], active="True", path=record["Path"], CHSUM_Flash=record["Checksum_Flash"] , CHSUM_EEPROM=record["Checksum_EEPROM"],time_now=datetime.now())

        if (i+1)%100==0:
            #remove last comma from parsed_values 
            parsed_values=parsed_values[:-1]
            cursor.execute("INSERT INTO \"Program\"(\"HDV\",\"PAP_date\",\"Actor\",\"Board\",\"Software\",\"Compilation_timedate\",\"Active\",\"Path\", \"CHSUM_Flash\", \"CHSUM_EEPROM\", \"Log_processed_timedate\"){}".format(parsed_values))
            conn.commit()
            parsed_values="VALUES"
            print("Záznamy {} - {} boli nahrané do databázy".format(i-99,i+1))


    parsed_values=parsed_values[:-1]
    cursor.execute("INSERT INTO \"Program\"(\"HDV\",\"PAP_date\",\"Actor\",\"Board\",\"Software\",\"Compilation_timedate\",\"Active\",\"Path\", \"CHSUM_Flash\", \"CHSUM_EEPROM\", \"Log_processed_timedate\"){}".format(parsed_values))
    print("Záznamy nahraté do databázy")
    conn.commit()

    cursor.close()
    conn.close()

    exit()    