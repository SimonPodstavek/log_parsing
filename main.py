import re
from log_classes import *
from datetime import datetime,date
import time
from os import path, access, R_OK
from database.session import *
from pprint import pprint
from msvcrt import getch



records_collection=[]
satisfying_records=[]

regex_expressions = {
    'SW_version_3G' : re.compile(r'^[A-Z]{4}_\d$'),
    'SW_version_2G' : re.compile(r'^[A-Z]{2}_\d$'),
    'safebytes' : re.compile(r'Programmovanie safe bytes\s*-\s*0x.{4}:\s*(.*)\s*-\s*OK'),
    'safebytes_repair' : re.compile(r'[A-F 0-9 \s]*'),
    'double_new_line_remove' : re.compile(r'\n{2,}'),
    'software_version' : re.compile(r'Verzia SW\s*-\s*(\S*)\s'),
    'any_software_version' : re.compile(r'^[A-Z]{2}}_\d$|^[A-Z]{4}_\d$'),
    'hex_date' : re.compile(r'HEX\s*:\s*[A-Z]:.*:\s*(\d{4}\.\d{2}\.\d{2}\.)\s*\d{2}:\d{2}:\d{2}'),
    'any' : re.compile(r'')
}






def collect_records_from_files(list_of_files:dict)->tuple:
    #regex that finds more than one new line and replaces it with one new line
    
    log_content,valid_files,records_list = [],[],[]
    files_with_warnings = {}

    #start checking if files are valid
    valid_files=list_of_files

    for _,file in enumerate(list_of_files):
        # check if file exists
        if not path.exists(file):
            files_with_warnings[file] = 100
            continue

        # check if user has sufficient permissions to read file
        if not access(file,R_OK):
            files_with_warnings[file] = 101
            continue

    #remove erroneous files from the list
    for _, file in files_with_warnings.items():
            valid_files.remove(_)

    if len(list_of_files) == 0:
        return 102, files_with_warnings
    

    mkay=[]
    for _, file in enumerate(valid_files):
        with open(file, 'r', encoding='utf-8-sig') as log:
            log_content.append(log.read().strip())
        records_list=log_content[_].split('-'*80)
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        records_list=list(filter(bool,records_list))
        mkay.extend(records_list)
    return mkay, files_with_warnings







def error_handler(record_id:int, error_number:int, error_message:str, required:bool,queried_string:str="N/A", requirement:str=regex_expressions['any']) -> 0 or str:
    selection_menu="------------------------- \n Vyberte si z nasledujúcich príkazov: \n Print záznamu -> P \n Nahradenie problémovej hodnoty -> I \n Preskočiť záznam -> ENTER \n Vynechať hodnotu v zázname -> E \n Preskočiť záznam, program ukončiť a zmeny uložiť -> ESC \n ------------------------- \n"

    print("Pri spracovaní záznamu č. {record_id} vznikla chyba: {error_number}. \nPopis chyby: {error_message} \nProblematický reťazec: {queried_string} \n".format(queried_string=queried_string, error_message=error_message,record_id=record_id,error_number=error_number))
    print(selection_menu)
    while True:
        key_pressed=getch()
        key_pressed.lower()
        match key_pressed:
            case b'p':
                print("\n"+records[record_id]+"\n"+selection_menu)
            case b'i':
                while True:
                    user_corrected_value=input("Pre navrat do menu \"RETURNME\". Zadajte prosím opravenú hodnotu: ")
                    if re.search(requirement,user_corrected_value) is not None:
                        print("Zmena bola akceptovaná. \n \n \n \n")
                        return user_corrected_value
                    elif user_corrected_value.upper() == "RETURNME":
                        print(selection_menu)
                        break
                    else:
                        print("Zadaná hodnota nevyhovuje požiadavkám, skúste to prosím znovu. Požiadavka: {}\n ".format(requirement.pattern))
            case b'\r':
                print("Záznam bol preskočený. \n")
                return

            case b'e':
                if not required:
                    return ""
                else:
                    print("Táto hodnota je povinná, prosím zadajte ju. \n")

            case b'\x1b':
                print("Ukončenie spracovania záznamov, ukladám údaje. \n")
                upload_records()
                break
            case _:
                print("Nesprávna klávesa, skúste to prosím znovu. \n")
    






def extract_function(record:str) -> str:
    raise('Not implemented yet')

def extract_actor_SW_Date_and_Board(record:str) -> tuple:
    raise('Not implemented yet')



# def extract_3G_version(record:str) -> tuple:

#     query = re.search(regex_expressions['SW_version_3G'], record)
#     if query is None:
#         version = error_handler(record, 106,"Prečítaná verzia SW nespĺňa kritéria pre SW ver. 3G",True, regex_expressions['SW_version_3G'])
#     else:
#         version = query

#     return (version)


def extract_2G_parameters(record_id:int,version_row:str) -> tuple:

    version = re.search(regex_expressions['SW_version_2G'], version_row)
    if version is None:
        repair = error_handler(record_id,  106,"Prečítaná verzia SW nespĺňa kritéria pre SW ver. 2G",True,version_row, regex_expressions['SW_version_2G'])
        if repair == None:
            return

    return (version)









def create_record_object(record:str) -> None or list:

    #Create new empty instance of record class
    records_collection.append(RecordBuilder())
    record_id=len(records_collection)-1

    #check if version is compatible with the script
    version_row = re.search(regex_expressions['software_version'], record)
    if version_row is not None:
        version_row=version_row.group(1)
    
    if version_row is None:
        version=error_handler(record_id, 105,"V zadanom zázname neexistuje verzia",True, "N/A",regex_expressions['any_software_version'])
        if version == None:
            return
        records_collection[record_id].setSoftware(response)



    if re.search(regex_expressions['SW_version_2G'], version_row) is not None:
        response=extract_2G_parameters(record_id,version_row)
        if response == None:
            return
        records_collection[record_id].setSoftware(response)
    elif re.search(regex_expressions['SW_version_3G'], version_row) is not None:
        print(1)
        pass
    else:
        version=error_handler(record_id, 106,"Zadaná verzia nespĺňa kritéria pre SW ver. 2G ani 3G",True,version_row, regex_expressions['any_software_version'])
        if version == None:
            return
        records_collection[record_id].setSoftware(response)
    

    safebytes=[]
    safebytes=re.search(regex_expressions['safebytes'], record)
    if safebytes is None:
        safebytes=error_handler(record_id, 108,"V zázname neboli nájdené safe bytes",True, "N/A",regex_expressions['safebytes_repair'])
    else:
        safebytes=safebytes.group(1).split()
    

    if safebytes[12] != "01" :
        pass
        # return



    #Get first line and split it by ; and assign it to Record instance
    programmed_time_and_date = record.split(';')
    records_collection[record_id].setPAP_date(datetime.strptime(programmed_time_and_date[0], '%Y.%m.%d %H:%M:%S'))

    #DO NOT APPLY TO VERSION 2.0 and aboove
    #Delete 0x from the beginning of the string on positions 4-6 and reverse the string to get HDV. Assign HDV to Record instance
    # HDV=([x for x in safebytes[7:4:-1]] )
    # records_collection[record_id].setHDV(''.join(HDV))

    actor_id=([x for x in safebytes[9:7:-1]] )
    actor_id.insert(0,'0x')
    records_collection[record_id].setActor(int(''.join(actor_id),16))



    board_id=([x for x in safebytes[4:1:-1]] )
    board_id.insert(0,'0x')
    board_id=int(''.join(board_id),16)
    required_length=8
    number_of_zeros=required_length-len(str(board_id))
    board_id=''.join(['V','0'*number_of_zeros,str(board_id)])
    records_collection[record_id].setBoard(board_id)


    records_collection[record_id].setSoftware(version_row)

    chsumFlash=''.join(['0x',safebytes[0]])
    records_collection[record_id].setChecksum_Flash(chsumFlash)
    
    chsumEEPROM=''.join(['0x',safebytes[1]])
    records_collection[record_id].setChecksum_EEPROM(chsumEEPROM)


    query=re.search(regex_expressions['hex_date'], record)
    if query is None:
        return 0

    compiled_date=datetime.strptime(query.group(1), '%Y.%m.%d.')
    records_collection[record_id].setCompilation_date(compiled_date)

    satisfying_records.append(record_id)




#go two levels up to get to the root directory
source = path.abspath(path.join(path.dirname(__file__), '..'))
# files=[r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log',r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log']
# files=[r'data\operation logs\2023\01\TM_PAP_2023-01.log',r'data\operation logs\2023\01\TU_PAP_2023-01.log']
files=[r'data\operation logs\2023\01\TM_PAP_2023-01.log']
# files=[r'data\operation logs\2023\01\TU_PAP_2023-01.log']
paths=[path.join(source, file) for file in files]





parsing_start_time = time.perf_counter()
def main():

    global records 
    records = collect_records_from_files(paths)[0]
    print(len(records))
    if records == 102:
        print('Chyba 102: V zadanom adresári sa nenachádzajú žiadne podporované súbory')
        return 0
    for record in records:
        create_record_object(record)

    upload_records()






def upload_records():
    if len(satisfying_records) == 0: 
        print('Chyba 107: Žiaden zo záznamov sa nepodarilo spracovať, teda sa nič sa nanahrá.')
        exit() 
        
        
    end_time = time.perf_counter()

    print("-------------------------")
    print("čas spracovania: {}\n".format(end_time-parsing_start_time))
    print('Spracované záznamy: {satisfying_records} / {records}\n'.format(satisfying_records=len(satisfying_records),records=len(records) ))
    print("Nespracované záznamy: {unprocessed} \n".format(unprocessed=len(records)-len(satisfying_records)))

    start_time=time.perf_counter()
    ma=[records_collection[_].to_dict() for _ in satisfying_records]
    end_time=time.perf_counter()
    print('obj -> dict time: {} \n'.format(end_time-start_time))


    start_time=time.perf_counter()
    collection=create_session().record
    collection.insert_many(ma)
    end_time=time.perf_counter()
    print("Vytvorenie relácie a upload: {}\n".format(end_time-start_time))
    exit()    




if __name__ == '__main__':
    main()


# # Datum a cas
# Prvy riadok

# 2023.01.09 12:49:45; PAP 2.0.221220; 273: [SK] HMH (OZP - Tibor Michálik)


# # Vcislo
# Výrobné číslo                   - V00000000

