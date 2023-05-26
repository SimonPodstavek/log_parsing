import re
import sys
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir
from log_classes import *
from handle_error import error_handler
from datetime import datetime
from pprint import pprint
from upload_records import upload_records



global record_object_collection

satisfying_records,record_object_collection=[],[]

regex_expressions = {
    'supported_file_types' : re.compile(r'.*_PAP_.*\.log'),
    'SW_version_3G' : re.compile(r'^[A-Z]{4}_\d$'),
    'SW_version_2G' : re.compile(r'^[A-Z]{2}_\d$'),
    'safebytes' : re.compile(r'Programmovanie safe bytes\s*-\s*0x.{4}:\s*(.*)\s*-\s*OK'),
    'safebytes_repair' : re.compile(r'[A-F 0-9 \s]*'),
    'double_new_line_remove' : re.compile(r'\n{2,}'),
    'software_version' : re.compile(r'Verzia SW\s*-\s*(\S*)\s'),
    'any_software_version' : re.compile(r'^[A-Z]{2}_\d$|^[A-Z]{4}_\d$'),
    'hex_date' : re.compile(r'HEX\s*:\s*[A-Z]:.*:\s*(\d{4}\.\d{2}\.\d{2}\.)\s*\d{2}:\d{2}:\d{2}'),
    'any' : re.compile(r'')
}


def collect_records_from_files(list_of_files:dict)->tuple:
    log_contents,valid_files,records_list,file_object_collection = [],[],[],[]

    #log_contents -> list of strings, each string is contents of a file
    #valid_files -> list of files that are valid
    #records_list -> list of records, each record is a list of strings
    #file_object_collection -> list of File objects


    #Assign list of all files to valid_files, so that we can remove erroneous files from the list later
    valid_files=list_of_files.copy()

    #check if files exist
    for _,file in enumerate(list_of_files):
        if not path.exists(file):
            valid_files.remove(file)
            print("Chyba 100: Súbor {} neexistuje.".format(file))
            continue

        # check if user has sufficient permissions to read contents of a file
        if not access(file,R_OK):
            valid_files.remove(file)
            print("Chyba 101: K suboru {} nemá klient dostatočné povolenia na čítanie súboru.".format(file))
            continue

    #If there aren't any valid files, exit
    if len(valid_files) == 0:
        print("Chyba 102: V zvolenom adresári sa nenachádzajú žiadne súbory.")
        sys.exit(102)

    #Read contents of all valid files
    for _, file in enumerate(valid_files):
        #open file and decode contents
        with open(file, 'rb') as log:
            log=log.read()

            try:
                if log[0] == 255:
                    log=log.decode('utf-16')
                else:     
                        log=log.decode('utf-8-sig')
            except:
                print("Chyba 112: Pre súbor {} nebolo nájdené podporované enkódovanie. FILE_SKIPPED".format(file))
                continue
        
        log_contents.append(log.strip())
        
    #Split contents of each file into individual records
        if re.compile(r'.*PAP.*\.log').search(file):
            records_list=log_contents[_].split('-'*80)
        else:
            print("Chyba 113: Súbor {} nie je log typu PAP. FILE_SKIPPED".format(file))
            continue

        #Remove double new lines and empty records
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        records_list=list(filter(bool,records_list))
        file_object_collection.append(File(records_list, file))
    return file_object_collection


def extract_function(record:str) -> str:
    raise('Not implemented yet')

def extract_actor_SW_Date_and_Board(record:str) -> tuple:
    raise('Not implemented yet')


def extract_2G_parameters(record_id:int,version_row:str) -> tuple:

    version = re.search(regex_expressions['SW_version_2G'], version_row)
    if version is None:
        response = error_handler(record_object_collection, record_id,  106,"Prečítaná verzia SW nespĺňa kritéria pre SW ver. 2G",True,version_row, regex_expressions['SW_version_2G'])
        if response == None or response == 111:
            return
        elif response == 111:
            return 111

    return (version.group(0))


def create_record_object(record:str, path:str) -> None or list:
    #Create new empty instance of record class
    record_object_collection.append(RecordBuilder())
    record_id=len(record_object_collection)-1

    record_object_collection[record_id].setContent(record)

    #check if version is compatible with the script
    version_row = re.search(regex_expressions['software_version'], record)
    if version_row is not None:
        version_row=version_row.group(1)
    
    if version_row is None:
        response=error_handler(record_object_collection, record_id, 105,"V zadanom zázname neexistuje verzia",True, "N/A",regex_expressions['any_software_version'])
        if response == None:
            return
        elif response == 111:
            return 111

        record_object_collection[record_id].setSoftware(response)
    elif re.search(regex_expressions['SW_version_2G'], version_row) is not None:
        response=extract_2G_parameters(record_id,version_row)
        if response == None:
            return
        record_object_collection[record_id].setSoftware(response)
    elif re.search(regex_expressions['SW_version_3G'], version_row) is not None:
        print("3G SW")
        return 
    else:
        version=error_handler(record_object_collection, record_id, 106,"Zadaná verzia nespĺňa kritéria pre SW ver. 2G ani 3G",True,version_row, regex_expressions['any_software_version'])
        if version == None:
            return
        elif response == 111:
            return 111
        record_object_collection[record_id].setSoftware(response)
    

    safebytes=[]
    safebytes=re.search(regex_expressions['safebytes'], record)
    if safebytes is None:
        safebytes=error_handler(record_object_collection, record_id, 108,"V zázname neboli nájdené safe bytes",True, "N/A",regex_expressions['safebytes_repair'])
        if safebytes == None:
            return
        elif response == 111:
            return 111
    else:
        safebytes=safebytes.group(1).split()
    

    if safebytes[12] != "01" :
        pass



    #Get first line and split it by ; and assign it to Record instance
    programmed_time_and_date = record.split(';')[0]
    original_date_format = datetime.strptime(programmed_time_and_date, '%Y.%m.%d %H:%M:%S')
    record_object_collection[record_id].setPAP_date(datetime.strftime(original_date_format, '%Y-%m-%d %H:%M:%S'))

    #DO NOT APPLY TO VERSION 2.0 and aboove
    # Delete 0x from the beginning of the string on positions 4-6 and reverse the string to get HDV. Assign HDV to Record instance

    # HDV=([x for x in safebytes[7:4:-1]] )
    # record_object_collection[record_id].setHDV(''.join(HDV))

    actor_id=([x for x in safebytes[9:7:-1]] )
    actor_id.insert(0,'0x')
    record_object_collection[record_id].setActor(int(''.join(actor_id),16))



    board_id=([x for x in safebytes[4:1:-1]] )
    board_id.insert(0,'0x')
    board_id=int(''.join(board_id),16)
    required_length=8
    number_of_zeros=required_length-len(str(board_id))
    board_id=''.join(['V','0'*number_of_zeros,str(board_id)])
    record_object_collection[record_id].setBoard(board_id)

    chsumFlash=''.join(['0x',safebytes[0]])
    record_object_collection[record_id].setChecksum_Flash(chsumFlash)
    
    chsumEEPROM=''.join(['0x',safebytes[1]])
    record_object_collection[record_id].setChecksum_EEPROM(chsumEEPROM)


    query=re.search(regex_expressions['hex_date'], record)
    if query is None:
        return 0

    old_compiled_date=datetime.strptime(query.group(1), '%Y.%m.%d.')

    record_object_collection[record_id].setCompilation_timedate(datetime.strftime(old_compiled_date, "%Y-%m-%d"))

    record_object_collection[record_id].setPath('/'.join(path.lower().split('\\')[-3:]))

    satisfying_records.append(record_object_collection[record_id])






def main():

    starting_path = abspath(join(dirname(__file__), '../data/operation logs/operational/2023'))
    paths=[]
    for root, directories, selected_files in walk(starting_path):
        if len(selected_files) != 0:
            for i, file in enumerate(selected_files):
                if regex_expressions['supported_file_types'].search(file) is not None:
                    paths.append(join(root,file))


    records_of_files = collect_records_from_files(paths)
    number_of_records = sum(file.getLength() for file in records_of_files)
    print(number_of_records)
    immediate_upload=False
    for file in records_of_files:
        path = file.getPath()
        for record in file.getRecords():
            if create_record_object(record,path) == 111:
                immediate_upload=True
                break

        if immediate_upload == True:
            break
    upload_records(satisfying_records,number_of_records)

if __name__ == '__main__':
    main()
