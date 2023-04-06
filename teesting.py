import re
from log_classes import *
from datetime import datetime
import time
from os import path, access, R_OK

records_collection=[]

regex_expressions = {
    'safebytes' : re.compile(r'Programmovanie safe bytes\s*-\s*0x0001:\s*(.*)\s*-\s*OK'),
    'double_new_line_remove' : re.compile(r'\n{2,}'),
    'software_version' : re.compile(r'Verzia SW\s*-\s*(.*)'),
    'accepted_version' : re.compile(r'^[A-Z]{2}_\d$'),
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








def create_record_object(record:str) -> dict:

    #check if version is compatible with the script
    version = re.search(regex_expressions['software_version'], record)
    if version is None:
        return 0

    if re.search(regex_expressions['accepted_version'], version.group(1)) is None:
        return 0

    safebytes=[]
    query=re.search(regex_expressions['safebytes'], record)
    if query is None:
        return 0
    else:
        query=query.group(1).split()
    safebytes=query
    

    if safebytes[12] != "02" :
        return 0


    #Create new empty instance of record class
    records_collection.append(RecordBuilder())
    record_id=len(records_collection)-1


    #Get first line and split it by ; and assign it to Record instance
    Programmed_time_and_date = record.split(';')[0].split()
    records_collection[record_id].setPAP_date(datetime.strptime(Programmed_time_and_date[0], '%Y.%m.%d'))
    records_collection[record_id].setPAP_time(datetime.strptime(Programmed_time_and_date[1], '%H:%M:%S').time())

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


    records_collection[record_id].setSoftware(version.group(1))

    chsumFlash=''.join(['0x',safebytes[0]])
    records_collection[record_id].setChecksum_Flash(chsumFlash)
    
    chsumEEPROM=''.join(['0x',safebytes[1]])
    records_collection[record_id].setChecksum_EEPROM(chsumEEPROM)


    query=re.search(regex_expressions['hex_date'], record)
    if query is None:
        return 0

    compiled_date=datetime.strptime(query.group(1), '%Y.%m.%d.')
    records_collection[record_id].setCompilation_date(compiled_date)


    records_collection[record_id].setContents(record)





source=r'C:\Users\Admin\Desktop'
# files=[r'Log analysis\data\operation logs\2023\01\TM_PAP_2023-01.log',r'Log analysis\data\operation logs\2023\01\VP_PAP_2023-01.log']
files=[r'Log analysis\data\operation logs\2023\01\TM_PAP_2023-01.log']
paths=[path.join(source, file) for file in files]




def main():
    start_time = time.perf_counter()

    records, warnings = collect_records_from_files(paths)
    print(len(records))
    if records == 102:
        print('Chyba 102: Žiadny subor nie je platný')
        return 0
    for record in records:
        create_record_object(record)
        
    end_time = time.perf_counter()

    print('time taken: {time_taken}'.format(time_taken=end_time-start_time))
    # print('first record board : {}'.format(records_collection[0].build().getBoard()))
    print('number of records: {record_len}'.format(record_len=len(records_collection)))
    print('warnings: {}'.format(warnings))
    return 0




if __name__ == '__main__':
    main()


# # Datum a cas
# Prvy riadok

# 2023.01.09 12:49:45; PAP 2.0.221220; 273: [SK] HMH (OZP - Tibor Michálik)


# # Vcislo
# Výrobné číslo                   - V00000000


# #Programovanie safebytes

# Programmovanie safe bytes       - 0x0001: 4C BF 00 00 00 11 01 23 11 01 00 00 02 54 4E 01 - OK

# # HDV
# Číslo HDV                       - 998040 - nezapísané do SafeBytes


# #Verzia

# Verzia SW                       - TY_1