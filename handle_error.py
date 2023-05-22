import reupload_records
from msvcrt import getch
from log_classes import *
import time
import sys
from database.upload_records import upload_records

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



def error_handler(record_object_collection:list, record_id:int , error_number:int, error_message:str, required:bool,queried_string:str="N/A", requirement:str=regex_expressions['any']) -> 0 or str:
    # return 0
    selection_menu="------------------------- \n Vyberte si z nasledujúcich príkazov: \n Print záznamu -> P \n Nahradenie problémovej hodnoty -> I \n Preskočiť záznam -> ENTER \n Vynechať hodnotu v zázname -> E \n  Ukončiť spracovanie a uložiť záznamy -> E \n ------------------------- \n"
    print("Pri spracovaní záznamu č. {record_id} vznikla chyba: {error_number}. \nPopis chyby: {error_message} \nProblematický reťazec: {queried_string} \n".format(queried_string=queried_string, error_message=error_message,record_id=record_id,error_number=error_number))
    print(selection_menu)
    while True:
        key_pressed=getch()
        key_pressed.lower()
        match key_pressed:
            case b'p':
                print("\n"+record_object_collection[record_id].getContent()+"\n"+selection_menu)
            case b'i':
                while True:
                    user_corrected_value=input("Pre navrat do menu \"RETURNME\". Zadajte prosím opravenú hodnotu: ")
                    if re.search(requirement,user_corrected_value) is not None:
                        print("Zmena bola akceptovaná. \n \n \n")
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
                return 111
            case _:
                print("Nesprávna klávesa, skúste to prosím znovu. \n")