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
regex_expressions.update({'PAP_date' : r'.*-{5,}\n(.*)\n.*'})



def collect_records_from_files(list_of_files:dict)->tuple:
    failed_files_counter=0
    log_contents,valid_files,records_list,file_object_collection = [],[],[],[]

    #log_contents -> list of strings, each string is contents of a file
    #valid_files -> list of files that are valid
    #records_list -> list of records, each record is a list of strings
    #file_object_collection -> list of File objects

    #Assign list of all files to valid_files, so that erroneous files can be removed from the list later
    valid_files=list_of_files.copy()

    #check if files exist
    for i,file in enumerate(list_of_files):
        if not path.exists(file):
            valid_files.remove(file)
            failed_files_counter+=1
            print("Chyba 100: Súbor {} neexistuje.".format(file))
            continue

        # check if user has sufficient permissions to read contents of a file
        if not access(file,R_OK):
            valid_files.remove(file)
            failed_files_counter+=1
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
                    log=log.decode('utf-8')
            except:
                print("Chyba 112: Pre súbor {} nebolo nájdené podporované enkódovanie. FILE_SKIPPED".format(file))
                failed_files_counter+=1
                continue
        
        log_contents = log.strip()
        
        #the following regex expressions are used to determine the type of log file
        #after the type is determined, the contents of the file are split into individual records, removing separators, keeping log header

        #PAP log
        if re.compile(r'.*pap.*\.(log|txt)').search(file.lower()):
            records_list=log_contents.split('-'*80)

        #KAM log or kamw log
        elif re.compile(r'.*kam.*\.(log|txt)').search(file.lower()):
            records_list = re.findall(r'.*#{60}\r?\n(.*)\r?\n#{60}.*([^#]*)',log_contents)   
            records_list = [''.join(x) for x in records_list]
              
        else:
            print("Chyba 113: Súbor {} nie je log typu KAM ani PAP. FILE_SKIPPED".format(file))
            failed_files_counter+=1
            continue

        #Remove double new lines and empty records
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        records_list=list(filter(bool,records_list))
        file_object_collection.append(File(records_list, file))
    return file_object_collection, failed_files_counter


def find_and_create_regex_expressions(record:list)->None:
    #find record creation date
    if re.search(regex_expressions['PAP_date'], record):
        pass
    else:
        print("Chýbajúci PAP_Date v zázname {} nebolo nájdené dátum vytvorenia. RECORD_SKIPPED".format(record))
        return None
    




def main():
    starting_path = abspath(join(dirname(__file__), '../../data/operation logs/2008'))
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
    
    records_of_files, failed_files = collect_records_from_files(paths)
    number_of_records = sum(file.getLength() for file in records_of_files)
    print("Počet prečítaných súborov: {} z celkového počtu: {}, úspešnosť: {}%".format(len(paths), failed_files+len(paths), 100*(len(paths)/(failed_files+len(paths)))))
    print("Počet nájdených záznamov (PAP + KAM): {}".format(number_of_records))



    






    with open('regex_constructor/regex_expressions.pickle', 'wb') as expressions_file:
        pickle.dump(regex_expressions, expressions_file)
if __name__ == '__main__':
    main()