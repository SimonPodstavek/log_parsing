import re
import sys
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir
import pickle

sys.path.append('../src')
from log_classes import File


# Load existing regex expressions
with open('regex_constructor/regex_expressions.pickle', 'rb') as expressions_file:
    regex_expressions=pickle.load(expressions_file)


# regex_expressions = {
#     'supported_file_types' : r'.*_PAP_.*\.log',
#     'SW_version_3G' : r'^[A-Z]{4}_\d$',
#     'SW_version_2G' : r'^[A-Z]{2}_\d$',
#     'safebytes' : r'Programmovanie safe bytes\s*-\s*0x.{4}:\s*(.*)\s*-\s*OK',
#     'safebytes_repair' : r'[A-F 0-9 \s]*',
#     'double_new_line_remove' : r'\n{2,}',
#     'software_version' : r'Verzia SW\s*-\s*(\S*)\s',
#     'any_software_version' : r'^[A-Z]{2}_\d$|^[A-Z]{4}_\d$',
#     'hex_date' : r'HEX\s*:\s*[A-Z]:.*:\s*(\d{4}\.\d{2}\.\d{2}\.)\s*\d{2}:\d{2}:\d{2}',
#     'any' : r''
# }


#merger regex_expressions with another dictionary
regex_expressions.update({'kamw_split' : r'#{60}\n.*#{60}'})
def collect_records_from_files(list_of_files:dict)->tuple:
    log_contents,valid_files,records_list,file_object_collection = [],[],[],[]

    #log_contents -> list of strings, each string is contents of a file
    #valid_files -> list of files that are valid
    #records_list -> list of records, each record is a list of strings
    #file_object_collection -> list of File objects


    #Assign list of all files to valid_files, so that we can remove erroneous files from the list later
    valid_files=list_of_files.copy()

    #check if files exist
    for i,file in enumerate(list_of_files):
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
    for i, file in enumerate(valid_files):
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
            records_list=log_contents[i].split('-'*80)
        elif re.compile(r'.*KAM.*\.log').search(file):
            records_list=log_contents[i].split('-'*60)
        elif re.compile(r'.*kamw.*\.log').search(file):
            # records_list=re.split(r'\n', log_contents[i])
            records_list=re.split(r'.*#{60}\r\n.*\r\n#{60}.*', log_contents[i])
            
        else:
            print("Chyba 113: Súbor {} nie je log typu KAM ani PAP. FILE_SKIPPED".format(file))
            continue

        #Remove double new lines and empty records
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        records_list=list(filter(bool,records_list))
        file_object_collection.append(File(records_list, file))
    return file_object_collection



def main():
    starting_path = abspath(join(dirname(__file__), '../../data/operation logs/'))
    paths=[]
    

    for root, directories, selected_files in walk(starting_path):
        if len(selected_files) != 0:
            for i, file in enumerate(selected_files):
                if re.compile(regex_expressions['any']).search(file) is not None:
                    paths.append(join(root,file))

    global record_paths
    if len(paths) == 0:
        print(print("Chyba 102: V adresári {} sa nenachádzajú žiadne súbory.".format(starting_path)))
        return 102
    

    records_of_files = collect_records_from_files(paths)
    number_of_records = sum(file.getLength() for file in records_of_files)
    print(number_of_records)


    with open('regex_constructor/regex_expressions.pickle', 'wb') as expressions_file:
        pickle.dump(regex_expressions, expressions_file)
if __name__ == '__main__':
    main()