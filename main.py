import re
import sys
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir
from log_classes import *
from handle_error import error_handler
from datetime import datetime, date
from pprint import pprint
import pickle
from upload_records import upload_records



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






def create_pap_record_object(record:list, path:str)->None or list:

    #Create new empty instance of record class
    # record_object = PAPRecordBuilder()
    # record_object.setContent(record)


    # parameter_found=False
    # try:
    #     response = re.search(regex_expressions['PAP_date'], record)
    #     response = response.group(0).strip()
    #     response = response.replace('. ', '.')
    # except:
    #     pass

    # for format in ('%Y.%m.%d %H:%M:%S','%Y.%m.%d %H:%M:%S;','%m/%d/%Y %H:%M:%S'):
    #     try:
    #         response = datetime.strptime(response, format)
    #         record_object.set_date(response)
    #         parameter_found=True
    #         break
    #     except:
    #         pass

    # if parameter_found == False:
    #         response = error_handler(record_object, 105,"V zadanom zázname neexistuje dátum a čas. Zadajte dátum a čas v formáte dd.mm.yyyy hh:mm:ss",True, "N/A",re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}\s\d{1,2}:\d{1,2}:\d{1,2}'))
    #         if response == None:
    #             return
    #         elif response == 111:
    #             return 111
    #         else:
    #             response = datetime.strptime(response, '%d.%m.%Y %H:%M:%S')
    #             parameter_found=True

    # record_object.set_date(response)
    # satisfying_records.append(record_object)

    return None





def create_kam_record_object(record:list, path:str)->None or list:

    #Create new empty instance of record class
    record_object = KAMRecordBuilder()
    record_object.set_content(record)

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



    #Find Actor name
    # parameter_found=False
    # try:
    #     response = re.findall(regex_expressions['KAM_actor'], record)
    #     #Select just first matching REGEX group
    #     response = ''.join(filter(None, response[0])).strip()
    #     #Remove closing parenthesis if they do not match opening parenthesis
    #     if '(' not in response:
    #         response = response.replace(')', '')
        
    #     record_object.set_date(response)
    #     parameter_found=True
    # except:
    #     pass

    # if parameter_found == False:
    #     response = error_handler(record_object, 105,"V zadanom zázname neexistuje Actor. Zadajte meno Actor-a",True, "N/A",re.compile(r'.*'))
    #     if response == None:
    #         return
    #     elif response == 111:
    #         return 111
    #     else:
    #         parameter_found=True
            
    # record_object.setActor(response)

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
            
    record_object.set_M_programmed_configuration(M_response)
    record_object.set_C_programmed_configuration(C_response)
    
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
            
    record_object.set_M_programmed_functionality(M_response)
    record_object.set_C_programmed_functionality(C_response)

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
    satisfying_records.append(record_object)


    return None


        









# def create_record_object(record:str, path:str) -> None or list:
#     #Create new empty instance of record class
#     record_object_collection.append(RecordBuilder())
#     record_id=len(record_object_collection)-1

#     record_object_collection[record_id].setContent(record)

#     #check if version is compatible with the script
#     version_row = re.search(regex_expressions['software_version'], record)
#     if version_row is not None:
#         version_row=version_row.group(1)
    
#     if version_row is None:
#         response=error_handler(record_object_collection, record_id, 105,"V zadanom zázname neexistuje verzia",True, "N/A",regex_expressions['any_software_version'])
#         if response == None:
#             return
#         elif response == 111:
#             return 111

#         record_object_collection[record_id].setSoftware(response)
#     elif re.search(regex_expressions['SW_version_2G'], version_row) is not None:
#         response=extract_2G_parameters(record_id,version_row)
#         if response == None:
#             return
#         record_object_collection[record_id].setSoftware(response)
#     elif re.search(regex_expressions['SW_version_3G'], version_row) is not None:
#         print("3G SW")
#         return 
#     else:
#         version=error_handler(record_object_collection, record_id, 106,"Zadaná verzia nespĺňa kritéria pre SW ver. 2G ani 3G",True,version_row, regex_expressions['any_software_version'])
#         if version == None:
#             return
#         elif response == 111:
#             return 111
#         record_object_collection[record_id].setSoftware(response)
    

#     safebytes=[]
#     safebytes=re.search(regex_expressions['safebytes'], record)
#     if safebytes is None:
#         safebytes=error_handler(record_object_collection, record_id, 108,"V zázname neboli nájdené safe bytes",True, "N/A",regex_expressions['safebytes_repair'])
#         if safebytes == None:
#             return
#         elif response == 111:
#             return 111
#     else:
#         safebytes=safebytes.group(1).split()
    

#     if safebytes[12] != "01" :
#         pass



#     #Get first line and split it by ; and assign it to Record instance
#     programmed_time_and_date = record.split(';')[0]
#     original_date_format = datetime.strptime(programmed_time_and_date, '%Y.%m.%d %H:%M:%S')
#     record_object_collection[record_id].setPAP_date(datetime.strftime(original_date_format, '%Y-%m-%d %H:%M:%S'))

#     #DO NOT APPLY TO VERSION 2.0 and aboove
#     # Delete 0x from the beginning of the string on positions 4-6 and reverse the string to get HDV. Assign HDV to Record instance

#     # HDV=([x for x in safebytes[7:4:-1]] )
#     # record_object_collection[record_id].setHDV(''.join(HDV))

#     actor_id=([x for x in safebytes[9:7:-1]] )
#     actor_id.insert(0,'0x')
#     record_object_collection[record_id].setActor(int(''.join(actor_id),16))



#     board_id=([x for x in safebytes[4:1:-1]] )
#     board_id.insert(0,'0x')
#     board_id=int(''.join(board_id),16)
#     required_length=8
#     number_of_zeros=required_length-len(str(board_id))
#     board_id=''.join(['V','0'*number_of_zeros,str(board_id)])
#     record_object_collection[record_id].setBoard(board_id)

#     chsumFlash=''.join(['0x',safebytes[0]])
#     record_object_collection[record_id].setChecksum_Flash(chsumFlash)
    
#     chsumEEPROM=''.join(['0x',safebytes[1]])
#     record_object_collection[record_id].setChecksum_EEPROM(chsumEEPROM)


#     query=re.search(regex_expressions['hex_date'], record)
#     if query is None:
#         return 0

#     old_compiled_date=datetime.strptime(query.group(1), '%Y.%m.%d.')

#     record_object_collection[record_id].setCompilation_timedate(datetime.strftime(old_compiled_date, "%Y-%m-%d"))

#     record_object_collection[record_id].setPath('/'.join(path.lower().split('\\')[-3:]))

#     satisfying_records.append(record_object_collection[record_id])






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
            if any(invalid_expression in  record.lower() for invalid_expression in ['prerušená', 'chyba', 'porušená', 'neplatná', 'error', 'interrupted', 'broken'] ):
                continue
            if 'pap' in  file.get_path().lower():
                # response = create_pap_record_object(record, file)
                pass
            else:
                if any(invalid_expression in  record.lower() for invalid_expression in ['------', '———————'] ):
                    continue
                create_kam_record_object(record, file)
            
            if response == 111:
                upload_records(satisfying_records,number_of_records)
                break
            
    upload_records(satisfying_records,number_of_records)

if __name__ == '__main__':
    main()
