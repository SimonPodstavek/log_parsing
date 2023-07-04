import re
from regex_constructor import find_regex

# mls = """

# C:\SW_AVR\M_VZ1\ZJ_03\VZ1#VM.HEX
# Command-line arguments count- OK - 3
# Programming [p], Verify [v] - p
# Input file name/date time   - C:\SW_AVR\M_VZ1\ZJ_03\VZ1#VM.HEX
#                               30.10.2009 09:53:45
# Programming Enable          - OK
# Chip erase                  - OK
# Programming Enable          - OK
# Device                      - ATmega 162 - 16 kB FLASH
# Programming FLASH           - OK
# Verify FLASH                - OK
# Input file name/date time   - C:\SW_AVR\M_VZ1\ZJ_03\VZ1#VM.EEP
#                               30.10.2009 09:53:45
# Programming EEPROM          - OK
# Verify EEPROM               - OK
# time: 7s516
# SW version                  - VM_3
# EquipeID                    - 1BEA
# LocoID                      - FFFFFF
# Programming safe bytes      - 8D 61 EA 1B FF FF FF 04 12 11 09 00 00 56 4D 03 - OK
# Verify safe bytes           - 8D 61 EA 1B FF FF FF 04 12 11 09 00 00 56 4D 03 - OK
# Writting fuse bytes         - L(FF) H(D9) E(EB) - OK
# Lock [l], Unlock [u]        - l
# Write lock bits             - OK
# """





# x = re.compile(r'(?:(?:HEX\s*:\s*[A-Z]:.*:\s*)|(?:Input file name\/date time.*\s*\n*\r*))(\d{1,4}\.\d{1,2}\.\d{1,4})')

# y = re.findall(x, mls)
# print(y)