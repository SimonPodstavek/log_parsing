from datetime import datetime

#File class contains list of records and path to the file
class File:
    def __init__(self,records,path) -> None:
        self.records = records
        self.path = path

    def getRecords(self):
        return self.records
    def getPath(self):
        return self.path
    def getLength(self):
        return len(self.records)


#Record class is a template for RecordBuilder
class Record:
    def __init__(self) -> None:
        self.HDV = None
        self.PAP_date = None
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
    def setPAP_date(self,PAP_date):
        self.record.PAP_date = PAP_date
        return self
    def setActor(self,actor):
        self.record.Actor = actor
        return self
    def setBoard(self,board_id):
        self.record.Board = board_id
        return self
    def setSoftware(self,software):
        self.record.Software = software
        return self
    def setChecksum_Flash(self,checksum_Flash):
        self.record.Checksum_Flash = checksum_Flash
        return self
    def setChecksum_EEPROM(self,checksum_EEPROM):
        self.record.Checksum_EEPROM = checksum_EEPROM
        return self
    def setCompilation_timedate(self,compilation_timedate):
        self.record.Compilation_timedate = compilation_timedate
        return self
    def setContent(self,content):
        self.record.content = content
        return self
    def setPath(self,path):
        self.record.path = path
        return self
    def build(self):
        return self.record
    
    def getContent(self):
        return self.record.content
    
    def to_dict(self):
        return {
            "HDV": self.record.HDV,
            "PAP_date": self.record.PAP_date,
            "Actor": self.record.Actor,
            "Board": self.record.Board,
            "Software": self.record.Software,
            "Checksum_Flash": self.record.Checksum_Flash,
            "Checksum_EEPROM": self.record.Checksum_EEPROM,
            "Compilation_timedate": self.record.Compilation_timedate,
            "Path": self.record.path
        }