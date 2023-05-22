import re
from os import path, access, R_OK, listdir, walk
from os.path import abspath, dirname, join, isfile, isdir

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

def main():
    starting_path = abspath(join(dirname(__file__), '../../data/operation logs/'))
    paths=[]

    for root, directories, selected_files in walk(starting_path):
        if len(selected_files) != 0:
            for i, file in enumerate(selected_files):
                if regex_expressions['any'].search(file) is not None:
                    paths.append(join(root,file))

        global record_paths

        records_of_files = collect_records_from_files(paths)
        number_of_records = sum(file.getLength() for file in records_of_files)
        print(number_of_records)
        immediate_upload=False
        for file in records_of_files:
            path = file.getPath()
            for record in file.getRecords():
                if create_record_object(record,path) == 111:
                    immediate_upload=True

            if immediate_upload == True:
                break	   

if __name__ == '__main__':
    main()