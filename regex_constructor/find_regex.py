import re
import sys
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir
import pickle
import pyperclip
from datetime import datetime, date

sys.path.append('../src')
from log_classes import File

# Load existing regex expressions
with open('regex_constructor/regex_expressions.pickle', 'rb') as file:
    regex_expressions=pickle.load(file)

# Load records used to detrmine regex expressions
with open('regex_constructor/regex_template_records.pickle', 'rb') as file:
    regex_template_records=pickle.load(file)




# regex_template_records={
#     'HDV': [],
#     'PAP_date': [],
#     'Actor': [],
#     'Board': [],
#     'Software': [],
#     'Compilation_timedate': [],
#     'CHSUM_Flash': [],
#     'CHSUM_EEPROM': [],   
#     'Config_timedate': [],
#     'Wheel_diameter': [],
#     'IRC': [],
#     'Functions': [],
#     'Spare_part': [],
# }




# regex_expressions={
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

# for key in regex_template_records.keys():
#     regex_expressions.update({key: '$^'})  

#USE THIS TO MANUALLY ADD OR REMOVE NEW REGEX EXPRESSIONS
# regex_expressions.pop('M_programmed_configuration')
# regex_template_records.update({'KAM_programmed_actor': []})
# regex_expressions.update({'KAM_programmed_actor': r'^$'})

# with open('regex_constructor/regex_expressions.pickle', 'wb') as file:
#     if len(regex_expressions) != 0:
#         pickle.dump(regex_expressions, file)
#         print('Regex výrazy boli uložené')

# with open('regex_constructor/regex_template_records.pickle', 'wb') as file:
#     if len(regex_template_records) != 0:
#         pickle.dump(regex_template_records, file)
#         print('Zdrojové súbory pre regex boli uložené')


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

        file_decoded=False
        with open(file, 'rb') as opened_file:
            try:
                #open file and try to decode its contents as UTF-16 or UTF-8
                log=opened_file.read()
                if log[0] == 255:
                    log = log.decode('utf-16')
                
                else:     
                    log = log.decode('utf-8-sig')

                file_decoded = True

            except:
                file_decoded = False
        opened_file.close()



        #if decoding fails, try to decode as windows-1250
        if not file_decoded:
            with open(file, 'r', encoding='windows-1250') as opened_file:
                try:
                    log = opened_file.read()
                    file_decoded = True
                except:
                    file_decoded = False
            opened_file.close()



        if not file_decoded:
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
            records_list = re.findall(r'#{60}\r?\n(.*)\r?\n#{60}([^#]*)',log_contents)
            records_list = [''.join(x) for x in records_list]
              
        else:
            print("Chyba 113: Súbor {} nie je log typu KAM ani PAP. FILE_SKIPPED".format(file))
            failed_files_counter+=1
            continue

        #Remove double new lines and empty records
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        records_list=list(filter(bool,records_list))
        records_list = [x for x in records_list if len(x.strip()) > 150] 
        file_object_collection.append(File(records_list, file))

    return file_object_collection, failed_files_counter



def validate_regex(missing_regex_name:str, record:list, regex_expressions:list,regex_template_records:list, validation = True)->None:
    print('*'*80+"\n {} \n \n CHÝBAJÚCI {}".format(record,missing_regex_name, ))
    # pyperclip.copy(regex_expressions[missing_regex_name])
    user_input_regex = input("Zadajte nový regex výraz:\n\r")
    regex_template_records[missing_regex_name].append(record)


    try:
        i=0
        while i < (len(regex_template_records[missing_regex_name])):
            query = re.findall(user_input_regex, regex_template_records[missing_regex_name][i])
            query = query[0]
            print('Nájdený parameter pre log {} : {}'.format(i, query))
            i+=1
    except:
        print("Chyba 114: Neplatný regex. Preskočiť záznam? (y/n):")
        if input().lower() != 'y':
            return validate_regex(missing_regex_name, record, regex_expressions,regex_template_records)
        else:
            regex_template_records[missing_regex_name].pop()
            return None

    if input("Regex výraz je platný. Uložiť? (y/n): ").lower() != 'n':
        return user_input_regex
    
    if input("Chcete výraz zadať znova? (y/n): ").lower() != 'n':
        return validate_regex(missing_regex_name, record, regex_expressions,regex_template_records)
    
    regex_template_records[missing_regex_name].pop()
    return None





# def find_pap_regex(record:list, file:File)->None:
#     #find record creation date
#     query = re.search(regex_expressions['PAP_date'], record)
#     if not query:
#         user_input_regex = validate_regex('PAP_date', record, regex_expressions, regex_template_records)
#         if user_input_regex is not None:
#             regex_expressions['PAP_date'] = user_input_regex


#     query = query.group(0).strip()
#     query = query.replace('. ', '.')
#     for format in ('%Y.%m.%d %H:%M:%S','%m/%d/%Y %H:%M:%S'):
#         try:
#             value = datetime.strptime(query, format)
#             # print(value)
#             break
#         except:
#             pass
        


#     # #find record actor
#     # query = re.findall(regex_expressions['PAP_actor'], record))









def find_kam_regex(record:list, file:File)->None:

    #KAM_date
    value = None
    query = re.search(regex_expressions['KAM_date'], record)  
    query = query.group(0).strip()
    query = re.sub(r'\s+', ' ', query)
    query = query.replace('. ', '.')
    for format in ('%d.%m.%Y %H:%M:%S','%m/%d/%Y %H:%M:%S'):
        try:
            datem = datetime.strptime(query, format)
            break
        except:
            pass

    if datem is None:
        raise ValueError('Pre KAM nebol nájdený platný dátum a čas.')


    # KAM_actor
    # response = re.findall(regex_expressions['KAM_actor'], record)
    # if len(response) == 0 :
    #     user_input_regex = validate_regex('KAM_actor', record, regex_expressions, regex_template_records)
    #     if user_input_regex is not None:
    #         regex_expressions['KAM_actor'] = user_input_regex
    # else:
    #     response = ''.join(filter(None, response[0])).strip()
    #     if '(' not in response:
    #         response = response.replace(')', '')
    #     if response is None:
    #         raise ValueError('Pre KAM nebol nájdený platný Actor.') 

    # KAM_HDV
    # response = re.findall(regex_expressions['HDV'], record)
    # if len(response) == 0 :
    #     user_input_regex = validate_regex('HDV', record, regex_expressions, regex_template_records)
    #     if user_input_regex is not None:
    #         regex_expressions['HDV'] = user_input_regex
    # else:
    #     response = ''.join(filter(None, response[0])).strip()
    #     if response is None:
    #         raise ValueError('Pre KAM nebol nájdený platný Actor.') 

        
    # KAM_Configuration
    # response = re.findall(regex_expressions['Programmed_configuration'], record)
    # if len(response) == 0 and datetime.date(datem) > date(2014,1,1):
    #     pass
    #     # user_input_regex = validate_regex('Programmed_configuration', record, regex_expressions, regex_template_records)
    #     # if user_input_regex is not None:
    #     #     regex_expressions['Programmed_configuration'] = user_input_regex
            
    # elif datetime.date(datem) > date(2014,1,1):
    #     M_response = ''.join(filter(None, response[0])).strip()
    #     if M_response is None:
    #         raise ValueError('Pre KAM nebola najdena konfiguracia.') 
        
    #     if len(response ) == 2:
    #         C_response = ''.join(filter(None, response[1])).strip()
    #     else:
    #         C_response = M_response

    #     print(M_response)
    #     print(C_response)

    # KAM_Configuration
    # response = re.findall(regex_expressions['Programmed_configuration'], record)
    # if len(response) == 0 and datetime.date(datem) > date(2014,1,1):
    #     pass
    #     # user_input_regex = validate_regex('Programmed_configuration', record, regex_expressions, regex_template_records)
    #     # if user_input_regex is not None:
    #     #     regex_expressions['Programmed_configuration'] = user_input_regex
            
    # elif datetime.date(datem) > date(2014,1,1):
    #     M_response = ''.join(filter(None, response[0])).strip()
    #     if M_response is None:
    #         raise ValueError('Pre KAM nebola najdena konfiguracia.') 
        
    #     if len(response ) == 2:
    #         C_response = ''.join(filter(None, response[1])).strip()
    #     else:
    #         C_response = M_response

    #     print(M_response)
    #     print(C_response)


    # KAM software
    # response = re.findall(regex_expressions['KAM_software'], record)
    # if len(response) == 0:
    #     # pass
    #     user_input_regex = validate_regex('KAM_software', record, regex_expressions, regex_template_records)
    #     if user_input_regex is not None:
    #         regex_expressions['KAM_software'] = user_input_regex
            
    # else:
    #     M_response = ''.join(filter(None, response[0])).strip()
    #     if M_response is None:
    #         raise ValueError('Pre KAM nebol nájdený software') 
        
    #     if len(response ) == 2:
    #         C_response = ''.join(filter(None, response[1])).strip()
    #     else:
    #         C_response = M_response

    #     print(M_response)
    #     print(C_response)


    # KAM programmed actor software
    response = re.findall(regex_expressions['KAM_programmed_actor'], record)
    if len(response) == 0:
        # pass
        user_input_regex = validate_regex('KAM_programmed_actor', record, regex_expressions, regex_template_records)
        if user_input_regex is not None:
            regex_expressions['KAM_programmed_actor'] = user_input_regex
            
    else:
        M_response = ''.join(filter(None, response[0])).strip()
        if M_response is None:
            raise ValueError('Pre KAM nebol nájdený actor programovania') 
        
        if len(response ) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response

        print(M_response)
        print(C_response)
   



    
def main(starting_path:str):

    print("Začínam spracovávať súbory v adresári: {}".format(starting_path))

    paths=[]
    for root, directories, selected_files in walk(starting_path):
        if len(selected_files) != 0:
            for i, file in enumerate(selected_files):
                if re.compile(regex_expressions['any']).search(file) is not None:
                    paths.append(join(root,file))

    if len(paths) == 0:
        print("Chyba 102: V adresári {} sa nenachádzajú žiadne súbory.".format(starting_path))
        return 102
    
    file_object_collection, failed_files = collect_records_from_files(paths)
    number_of_records = sum(file.get_length() for file in file_object_collection)
    print("Počet prečítaných súborov: {} z celkového počtu: {}, úspešnosť: {}%".format(len(paths), failed_files+len(paths), 100*(len(paths)/(failed_files+len(paths)))))
    print("Počet nájdených záznamov (PAP + KAM): {}".format(number_of_records))



    # find just first occurence of regex expression
    i=0
    for file in file_object_collection:
        for record in file.get_records():
            if any(invalid_expression in  record.lower() for invalid_expression in ['prerušená', 'chyba', 'porušená', 'neplatná', 'error', 'interrupted', 'Consistency of configuration data','broken'] ):
                continue
            if 'pap' in  file.get_path().lower():
                pass
                # find_pap_regex(record, file)
            else:
                if any(invalid_expression in  record.lower() for invalid_expression in ['------', '———————'] ):
                    continue
                # pass
                find_kam_regex(record, file)



    with open('regex_constructor/regex_expressions.pickle', 'wb') as file:
        if len(regex_expressions) == 0:
            return None
        pickle.dump(regex_expressions, file)
        print('Regex výrazy boli uložené')

    with open('regex_constructor/regex_template_records.pickle', 'wb') as file:
        if len(regex_template_records) == 0:
            return None
        pickle.dump(regex_template_records, file)
        print('Zdrojové súbory pre regex boli uložené')


if __name__ == '__main__':
    main(abspath(join(dirname(__file__), '../../data/operation logs')))