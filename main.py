import mysql.connector
from random import choices,randint,randrange
from string import ascii_uppercase
import datetime
import time
import tkinter as tk


with open(r"C:\Users\Admin\Desktop\Log analysis\data\operation logs\2023\03\TM_PAP_2023-03.log", "r",encoding='utf-8') as f:
    print(repr(f.read()))
    f.close()


# db =  mysql.connector.connect(
#     host='192.168.1.161',
#     user='.',
#     passwd='.',
#     database='sys'
# )

# db =  mysql.connector.connect(
#     host='127.0.0.1',
#     user='root',
#     passwd='v/y*s#o&k@e}t2a3t5r7y1.',
#     database='company'
# )


# db =  mysql.connector.connect(
#     host='192.168.1.11',
#     user='test',
#     passwd='.',
#     database='company'
# )



# number_of_records=50000
# dvs,value,date,customer=[],[],[],[]
# for x in range(number_of_records):
#     dvs.append(''.join(choices(ascii_uppercase, k=3)))
#     value.append(randint(0,99))
#     date.append(datetime.date(2000, 1, 1) + datetime.timedelta(days=randrange(8300)))
#     customer.append(randint(6,9))




# Q1="INSERT INTO `hmhtst`(`hdv`,`valucka`,`datumik`,`technik`)VALUES"
# for x,_ in enumerate(dvs):
#     Q1+="('{}',{},'{}',{}),".format(dvs[x],value[x],date[x],customer[x])
# Q1=Q1[:-1]

# print("Text generated, commiting.")



# mycursor = db.cursor()
# start = time.time()
# mycursor.execute(Q1)
# db.commit()

# end = time.time()
# print("Time taken:{}".format(end-start))
# db.close()

# root = tk.Tk()

# root.geometry("500x500")
# root.title("Test1")

# root.mainloop()

import re

#collect all the data from the list with the paths and file names. E.g. [C:\Users\Simon\Desktop\Analýza Logov\Prevádzkové logy\2017\01\VS_PAP.log]
def collect_data_from_file_location(list_of_files):
    data = []
    log = []
    for _, file in enumerate(list_of_files):
        data.append(open(file, 'r').read())
        record=data[_].split('--------------------------------------------------------------------------------')
        log.append([re.sub(r'\n{2,}', '\n', x) for x in record])
    return log[0]

def get_HDV_data(log):
    pattern = re.compile(r'(HDV|HKV)\s*-\s*(\d+)')
    HDV_data = []

    i=0
    for record in log:
        match=re.search(pattern, record)
        if match:
            HDV_data.append([i,match[2]])
        i+=1
    return HDV_data
#write regex to check for string that starts with some chatacters and continues with HDV ot HKV, continues with some amout of empty spaces, than - and after that number I want to get

#format print, so it will return wieh new line instead of \n without looping
paths=['C:\\Users\\Simon\\Desktop\\Analýza Logov\\Prevádzkové logy\\2017\\01\\VS_PAP.log']
print (get_HDV_data(collect_data_from_file_location(paths)))

#remove empty lines from the string