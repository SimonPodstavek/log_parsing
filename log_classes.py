from datetime import datetime

#File class contains list of records and path to the file
class File:
    def __init__(self,records,path) -> None:
        self.records = records
        self.path = path

    def get_records(self):
        return self.records
    def get_path(self):
        return self.path
    def get_length(self):
        return len(self.records)


#Record class is a template for RecordBuilder
class Record:
    def __init__(self) -> None:
        self.HDV = None
        self.date = None
        self.PAP_time = None
        self.Actor = None
        self.Board = None
        self.Software = None
        self.Checksum_Flash = None
        self.Checksum_EEPROM = None
        self.Compilation_timedate = None
        self.path = None
        self.content = None

#New empty instance of record class
class RecordBuilder :
    def __init__(self) -> None:
        self.record = Record()
    def setHDV(self,HDV):
        self.record.HDV = HDV
        return self
    def set_date(self,date):
        self.record.date = date
        return self
    def set_actor(self,actor):
        self.record.Actor = actor
        return self
    def set_board(self,board_id):
        self.record.Board = board_id
        return self
    def set_software(self,software):
        self.record.Software = software
        return self
    def set_checksum_Flash(self,checksum_Flash):
        self.record.Checksum_Flash = checksum_Flash
        return self
    def set_checksum_EEPROM(self,checksum_EEPROM):
        self.record.Checksum_EEPROM = checksum_EEPROM
        return self
    def set_compilation_timedate(self,compilation_timedate):
        self.record.Compilation_timedate = compilation_timedate
        return self
    def set_content(self,content):
        self.record.content = content
        return self
    def set_path(self,path):
        self.record.path = path
        return self
    def build(self):
        return self.record
    
    def get_content(self):
        return self.record.content
    
    def get_path(self):
        return self.record.path  
    
    def to_dict(self):
        return {
            "HDV": self.record.HDV,
            "date": self.record.date,
            "Actor": self.record.Actor,
            "Board": self.record.Board,
            "Software": self.record.Software,
            "Checksum_Flash": self.record.Checksum_Flash,
            "Checksum_EEPROM": self.record.Checksum_EEPROM,
            "Compilation_timedate": self.record.Compilation_timedate,
            "Path": self.record.path
        }