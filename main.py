import re
import sys
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir
from classes.log_classes import *
from classes.safebytes_coordinates import *
from utils.handle_error import *
from datetime import datetime, date
from pprint import pprint
import pickle
# from upload_records import upload_records



# global record_object_collection

satisfying_records=[]

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

with open('regex_constructor/regex_expressions.pickle', 'rb') as file:
    regex_expressions = pickle.load(file)
    for key in regex_expressions.keys():
        regex_expressions[key] = re.compile(regex_expressions[key])



def collect_records_from_files(list_of_files:dict)->tuple:
    failed_files_counter = 0
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
            print("Chyba 113: Súbor {} nie je log typu KAM, kamw ani PAP. FILE_SKIPPED".format(file))
            failed_files_counter+=1
            continue

        #Remove double new lines and empty records
        records_list=[re.sub(regex_expressions['double_new_line_remove'], '\n', x).strip() for x in records_list]
        #Remove empty records
        records_list=list(filter(bool,records_list))
        #Remove records that are shorter than 151 characters
        records_list = [x for x in records_list if len(x.strip()) > 150] 
        
        file_object_collection.append(File(records_list, file))


    return file_object_collection, failed_files_counter




z = 0

def create_pap_record_object(record:list, path:str)->None or list:
    global z
    # Create new empty instance of record class
    record_object = PAPRecordBuilder()
    record_object.set_content(record)

    safebytes = None

    #Find timestamp programmed
    parameter_found=False
    try:
        response = re.search(regex_expressions['PAP_date'], record)
        response = response.group(0).strip()
        response = response.replace('. ', '.')
    except:
        pass

    for format in ('%Y.%m.%d %H:%M:%S','%Y.%m.%d %H:%M:%S;','%m/%d/%Y %H:%M:%S'):
        try:
            response = datetime.strptime(response, format)
            record_object.set_date(response)
            parameter_found=True
            break
        except:
            pass

    if parameter_found == False:
            response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum a čas. Zadajte dátum a čas v formáte dd.mm.yyyy hh:mm:ss",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}'))
            if response == None:
                return
            elif response == 111:
                return 111
            else:
                response = datetime.strptime(response, '%d.%m.%Y %H:%M:%S')
                parameter_found=True
    record_object.set_date(response)

    #Find software
    parameter_found=False
    try:
        response = re.findall(regex_expressions['PAP_software'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        response = response.strip()
        
        record_object.set_software(response)
        parameter_found=True
        record_object.set_software(response)
    except:
        return None




    #Get safebytes generation
    software = record_object.get_software()
    generation = None
    if re.match(r'^.{2}_.{1,2}$', software):
        generation = 2
    elif re.match(r'^.{4}_.{1,2}$', software):
        generation = 3
    else:  
        if software != "noname" and software != "_0":
            print("SW nie je 2G ani 3G, preskakujem záznam")
            z+=1
        return None
    



    #Find safebytes
    parameter_found=False
    try:
        response = re.findall(regex_expressions['PAP_safebytes'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        safebytes = response.strip().split(' ')
        parameter_found=True
    except:
        pass

    if parameter_found == False:
        
        response = error_handler(record_object, 105,"V zadanom zázname neexistujú safebytes. Zadajte safebytes",True, "N/A",re.compile(r'^[A-Za-z]{2,4}_[0-9]$'))
        if response == None:
            return
        elif response == 111:
            return 111
        else:
            safebytes = response.strip().split(' ')
            parameter_found=True   



    #Get safebytes encoded version, and then map it with safebyte_versions dictionary onto safebytes subversions.
    # This creates an edition consisting of generation and safebytes version e.g. [2][1]is 1st version of 2nd generation 
    version = None
    try:
        if generation == 2:
                version = safebyte_versions[int(safebytes[12], 16)]
        elif generation == 3:
            version = safebyte_versions[int(safebytes[0], 16)]     
    except:
        return None



    #Get HDV from safebytes
    HDV = safebytes[safebyte_locations[generation][version].get_HDV()]
    HDV = ''.join(HDV)
    record_object.set_HDV(HDV)

    #Get actor ID from safebytes
    actor = safebytes[safebyte_locations[generation][version].get_actor()]
    actor = ''.join(actor)
    record_object.set_actor(actor)

    #Get BOARD from safebytes
    board = safebytes[safebyte_locations[generation][version].get_board()]
    board = ''.join(board)
    record_object.set_board(board)











    






    satisfying_records.append(record_object)


    return None








def create_kam_record_object(record:list, path:str)->None or list:

    #Create new empty instance of record class
    record_object = KAMRecordBuilder()
    record_object.set_content(record)


    #Find safebytes
    parameter_found=False
    try:
        safebytes = re.findall(regex_expressions['HDV'], record)
        #Select just first matching REGEX group
        safebytes = ''.join(filter(None, safebytes[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        safebytes = safebytes.strip()
        
        parameter_found=True
    except:
        pass

    if parameter_found == False:
        response = error_handler(record_object, 105,"V zadanom zázname sa nenachádzajú safebytes Zadajte Safebytes vo formáte XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX",True, "N/A",re.compile(r'(?:[A-F,0-9]{2}\s{1})*[A-F,0-9]{2}'))
        if response == None:
            return
        elif response == 111:
            return 111
        else:
            parameter_found=True
            


    #Find KAM Config date
    parameter_found=False
    try:
        response = re.search(regex_expressions['KAM_date'], record)  
        response = response.group(0).strip()
        response = re.sub(r'\s+', ' ', response)
        response = response.replace('. ', '.')
    except:
        pass

    for format in ('%d.%m.%Y %H:%M:%S','%m/%d/%Y %H:%M:%S'):
        try:
            response = datetime.strptime(response, format)
            record_object.set_config_timedate(response)
            parameter_found=True
            break
        except:
            pass


    if parameter_found == False:
        response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum a čas. Zadajte dátum a čas v formáte dd.mm.yyyy hh:mm:ss",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}'))
        if response == None:
            return
        elif response == 111:
            return 111
        else:
            response = datetime.strptime(response.strip(), '%d.%m.%Y %H:%M:%S')
            parameter_found=True

    record_object.set_config_timedate(response)



    #Find KAM Actor
    parameter_found = False
    M_response = ''
    C_response = ''
    try:
        response = re.findall(regex_expressions['KAM_actor'],record)
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response
        parameter_found = True
    except:
        pass

    if parameter_found == False and datetime.date(record_object.get_config_timedate()) > date(2014,1,1):
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza osoba konajúca konfiguráciu. Zadajte Actora pre kanál M",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza osoba konajúca konfiguráciu. Zadajte Actora pre kanál C (Ak je totožný ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_configuration(M_response)
    record_object.set_C_configuration(C_response)



    #Find HDV (Locomotive ID)
    parameter_found=False
    try:
        response = re.findall(regex_expressions['HDV'], record)
        #Select just first matching REGEX group
        response = ''.join(filter(None, response[0])).strip()
        #Remove closing parenthesis if they do not match opening parenthesis
        response = response.strip()
        
        record_object.set_HDV(response)
        parameter_found=True
    except:
        pass

    if parameter_found == False:
        response = error_handler(record_object, 105,"V zadanom zázname neexistuje HDV. Zadajte HDV vo formáte XXX-XXX alebo XXXX-XXX",True, "N/A",re.compile(r'.*-.*'))
        if response == None:
            return
        elif response == 111:
            return 111
        else:
            parameter_found=True
            
    record_object.set_HDV(response)


    #Find KAM Configuration (Configuration has been used in the majority of protocols since 2014)
    parameter_found = False
    M_response = ''
    C_response = ''
    try:
        if datetime.date(record_object.get_config_timedate()) > date(2014,1,1):
            response = re.findall(regex_expressions['KAM_configuration'],record)
            M_response = ''.join(filter(None, response[0])).strip()
            if len(response) == 2:
                C_response = ''.join(filter(None, response[1])).strip()
            else:
                C_response = M_response
            parameter_found = True
    except:
        pass

    if parameter_found == False and datetime.date(record_object.get_config_timedate()) > date(2014,1,1):
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza konfigurácia. Zadajte konfiguráciu pre kanál M",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza konfigurácia. Zadajte konfiguráciu pre kanál C (Ak je totožna ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_configuration(M_response)
    record_object.set_C_configuration(C_response)
    
    # Find KAM Software
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_software'],record)
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response
        parameter_found = True
    except:
        pass

    if parameter_found == False:
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza konfigurácia. Zadajte konfiguráciu pre kanál M",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza konfigurácia. Zadajte konfiguráciu pre kanál C (Ak je totožna ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_programmed_software(M_response)
    record_object.set_C_programmed_software(C_response)

    # # Find KAM programmed actor
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_programmed_actor'],record)
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response
        parameter_found = True
    except:
        pass

    if parameter_found == False:
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza účastník progranovania (Actor). Zadajte Actor pre kanál M",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza účastník progranovania (Actor). Zadajte Actor pre kanál C (Ak je totožný ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
  
    record_object.set_M_programmed_actor(M_response)
    record_object.set_C_programmed_actor(C_response)


    # Find KAM board number
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_board_number'],record)
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response
        parameter_found = True
    except:
        pass

    if parameter_found == False:
        M_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza číslo dosky. Zadajte číslo dosky pre kanál M",False, "N/A",re.compile(r'.*'))
        C_response = error_handler(record_object, 105,"V zadanom zázname sa nenachádza číslo dosky. Zadajte číslo dosky pre kanál C (Ak je totožný ako kanál M, zadajte \'-\'). ",False, "N/A",re.compile(r'.*'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = M_response

        parameter_found=True
            
    record_object.set_M_programmed_board(M_response)
    record_object.set_C_programmed_board(C_response)



    #Find KAM Functionality (Functionality has been used in some of protocols since 2014)
    parameter_found = False
    M_response = ''
    C_response = ''
    try:
        if datetime.date(record_object.get_config_timedate()) > date(2014,1,1):
            response = re.findall(regex_expressions['KAM_functionality'],record)
            M_response = ''.join(filter(None, response[0])).strip()
            if len(response) == 2:
                C_response = ''.join(filter(None, response[1])).strip()
            else:
                C_response = M_response
            parameter_found = True
    except:
        pass
            
    record_object.set_M_functionality(M_response)
    record_object.set_C_functionality(C_response)

    #Find KAM programmed date
    parameter_found=False
    M_response=''
    try:
        response = re.findall(regex_expressions['KAM_programmed_date'], record)  
        response = [re.sub(r'\s+', ' ', x.strip()) for x in response]
        response = [x.replace('. ', '.') for x in response]
        M_response = response[0] 
        if len(response) == 2:
            C_response = response[1] 
    except:
        pass

    for format in ('%d.%m.%Y','%m/%d/%Y'):
        try:
            M_response = datetime.strptime(M_response, format).date()
            record_object.set_M_programmed_date(M_response)
            parameter_found = True
            break
        except:
            pass

    for format in ('%d.%m.%Y','%m/%d/%Y'):
        try:
            C_response = datetime.strptime(C_response, format).date()
            record_object.set_C_programmed_date(C_response)
            break
        except:
            pass


    if parameter_found == False:
        M_response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum programovania pre kanál M. Zadajte dátum vo formáte dd.mm.yyyy",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
        C_response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum programovania pre kanál C. Zadajte dátum vo formáte dd.mm.yyyy (Ak je totožný ako kanál M, zadajte \'-\').",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
        if M_response == None:
            return
        elif M_response == 111:
            return 111
        else:
            M_response = datetime.strptime(M_response.strip(), '%d.%m.%Y')
        if C_response == None:
            return
        elif C_response == 111:
            return 111
        elif C_response == '-':
            C_response = datetime.strptime(M_response.strip(), '%d.%m.%Y')
            
        record_object.set_M_programmed_date(M_response)
        record_object.set_C_programmed_date(C_response)

    #Find KAM spare part 
    parameter_found = False
    try:
        response = re.findall(regex_expressions['KAM_spare_part'],record)
        M_response = ''.join(filter(None, response[0])).strip()
        if len(response) == 2:
            C_response = ''.join(filter(None, response[1])).strip()
        else:
            C_response = M_response
        parameter_found = True
        record_object.set_M_spare_part(M_response)
        record_object.set_C_spare_part(C_response)
    except:
        pass


    # If there's not an error while building object, append it to satisfying records
    satisfying_records.append(record_object)


    return None


        





def main():

    starting_path = abspath(join(dirname(__file__), '../data/operation logs/'))
    print("Začínam spracovávať súbory v adresári: {}".format(starting_path))
    paths=[]
    for root, directories, selected_files in walk(starting_path):
        if len(selected_files) != 0:
            for i, file in enumerate(selected_files):
                if regex_expressions['any'].search(file) is not None:
                    paths.append(join(root,file))

    if len(paths) == 0:
        print("Chyba 102: V adresári {} sa nenachádzajú žiadne súbory.".format(starting_path))
        return 102

    file_object_collection, failed_files = collect_records_from_files(paths)
    number_of_records = sum(file.get_length() for file in file_object_collection)
    print("Počet prečítaných súborov: {} z celkového počtu: {}, úspešnosť: {}%".format(len(paths), failed_files+len(paths), 100*(len(paths)/(failed_files+len(paths)))))
    print("Počet nájdených záznamov (PAP + KAM): {}".format(number_of_records))    

    i=0

    for file in file_object_collection:
        for record in file.get_records():
            response = None
            if any(invalid_expression in  record.lower() for invalid_expression in ['mazanie','prerušená', 'chyba', 'porušená', 'neplatná', 'error', 'interrupted', 'broken'] ):
                continue
            if 'pap' in  file.get_path().lower():
                response = create_pap_record_object(record, file)
                pass
            else:
                if any(invalid_expression in  record.lower() for invalid_expression in ['------', '———————'] ):
                    continue
                # create_kam_record_object(record, file)
                pass
            
            if response == 111:
                pass
                # upload_records(satisfying_records,number_of_records)
                break
            
    upload_records(satisfying_records,number_of_records)

if __name__ == '__main__':
    main()
