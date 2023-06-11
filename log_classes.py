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


#Record class is a template for PAPRecordBuilder
class PAPRecord:
    def __init__(self) -> None:
        self.HDV = None
        self.date = None
        self.PAP_time = None
        self.actor = None
        self.board = None
        self.software = None
        self.checksum_Flash = None
        self.checksum_EEPROM = None
        self.compilation_timedate = None
        self.path = None
        self.content = None

#Record class is a template for KAMRecordBuilder
class KAMRecord:
    def __init__(self) -> None:
        self.HDV = None
        self.config_timedate = None
        self.M_programmed_date = None
        self.M_programmed_actor = None
        self.M_programmed_software = None
        self.M_programmed_board = None
        self.M_programmed_functionality = None
        self.M_programmed_configuration = None
        self.C_programmed_date = None
        self.C_programmed_actor = None
        self.C_programmed_software = None
        self.C_programmed_board = None
        self.C_programmed_functionality = None
        self.C_programmed_configuration = None
        self.spare_part = None
        self.path = None
        self.content = None

#New empty instance of PAP record class
class PAPRecordBuilder :
    def __init__(self) -> None:
        self.record = PAPRecord()
    def set_HDV(self,HDV):
        self.record.HDV = HDV
        return self
    def set_date(self,date):
        self.record.date = date
        return self
    def set_actor(self,actor):
        self.record.actor = actor
        return self
    def set_board(self,board_id):
        self.record.board = board_id
        return self
    def set_software(self,software):
        self.record.software = software
        return self
    def set_checksum_Flash(self,checksum_Flash):
        self.record.checksum_Flash = checksum_Flash
        return self
    def set_checksum_EEPROM(self,checksum_EEPROM):
        self.record.checksum_EEPROM = checksum_EEPROM
        return self
    def set_compilation_timedate(self,compilation_timedate):
        self.record.compilation_timedate = compilation_timedate
        return self
    def set_content(self,content):
        self.record.content = content
        return self
    def set_path(self,path):
        self.record.path = path
        return self
    
    #get parameters
    def get_HDV(self):
        return self.record.HDV
    def get_date(self):
        return self.record.date
    def get_actor(self,):
        return self.record.actor    
    def get_board(self):
        return self.record.board
    def get_software(self):
        return self.record.software
    def get_checksum_Flash(self):
        return self.record.checksum_Flash 
    def get_checksum_EEPROM(self):
        return self.record.checksum_EEPROM 
    def get_compilation_timedate(self):
        return self.record.compilation_timedate
    def get_content(self):
        return self.record.content
    def get_path(self):
        return self.record.path  
    def build(self):
        return self.record
    


    def to_dict(self):
        return {
            "date": self.record.date,
            "Actor": self.record.Actor,
            "Board": self.record.Board,
            "Software": self.record.Software,
            "Checksum_Flash": self.record.Checksum_Flash,
            "Checksum_EEPROM": self.record.Checksum_EEPROM,
            "Compilation_timedate": self.record.Compilation_timedate,
            "Path": self.record.path
        }
    

#New empty instance of KAM record class
class KAMRecordBuilder :
    def __init__(self) -> None:
        self.record = KAMRecord()
    def set_HDV(self,HDV):
        self.record.HDV = HDV
        return self
    def set_config_timedate(self,config_timedate):
        self.record.config_timedate = config_timedate
        return self
    def set_M_programmed_date(self,M_programmed_date):
        self.record.M_programmed_date = M_programmed_date
        return self
    def set_M_programmed_actor(self,M_programmed_actor):
        self.record.M_programmed_actor = M_programmed_actor
        return self
    def set_M_programmed_software(self,M_programmed_software):
        self.record.M_programmed_software = M_programmed_software
        return self
    def set_M_programmed_board(self,M_programmed_board):
        self.record.M_programmed_board = M_programmed_board
        return self
    def set_M_programmed_functionality(self,M_programmed_functionality):
        self.record.M_programmed_functionality = M_programmed_functionality
        return self
    def set_M_programmed_configuration(self,M_programmed_configuration):
        self.record.M_programmed_configuration = M_programmed_configuration
        return self
    def set_C_programmed_date(self,C_programmed_date):
        self.record.C_programmed_date = C_programmed_date
        return self
    def set_C_programmed_actor(self,C_programmed_actor):
        self.record.C_programmed_actor = C_programmed_actor
        return self
    def set_C_programmed_software(self,C_programmed_software):
        self.record.C_programmed_software = C_programmed_software
        return self
    def set_C_programmed_board(self,C_programmed_board):
        self.record.C_programmed_board = C_programmed_board
        return self
    def set_C_programmed_functionality(self,C_programmed_functionality):
        self.record.C_programmed_functionality = C_programmed_functionality
        return self
    def set_C_programmed_configuration(self,C_programmed_configuration):
        self.record.C_programmed_configuration = C_programmed_configuration
        return self
    def set_spare_part(self,spare_part):
        self.record.spare_part = spare_part
        return self
    def set_content(self,content):
        self.record.content = content
        return self
    def set_path(self,path):
        self.record.path = path
        return self
    
    #get parameters
    def get_HDV(self):
        return self.record.HDV
    def get_config_timedate(self):
        return self.record.config_timedate
    def get_M_programmed_date(self):
        return self.record.M_programmed_date
    def get_M_programmed_actor(self):
        return self.record.M_programmed_actor
    def get_M_programmed_software(self):
        return self.record.M_programmed_software
    def get_M_programmed_board(self):
        return self.record.M_programmed_board
    def get_M_programmed_functionality(self):
        return self.record.M_programmed_functionality
    def get_M_programmed_configuration(self):
        return self.record.M_programmed_configuration
    def get_C_programmed_date(self):
        return self.record.C_programmed_date
    def get_C_programmed_actor(self):
        return self.record.C_programmed_actor
    def get_C_programmed_software(self):
        return self.record.C_programmed_software
    def get_C_programmed_board(self):
        return self.record.C_programmed_board
    def get_C_programmed_functionality(self):
        return self.record.C_programmed_functionality
    def get_C_programmed_configuration(self):
        return self.record.C_programmed_configuration
    def get_spare_part(self):
        return self.record.spare_part
    def get_content(self):
        return self.record.content
    def get_path(self):
        return self.record.path  
    
    def build(self):
        return self.record
    def KAM_to_dict(self):
        return {
            "HDV": self.record.HDV,
            "Config_timedate": self.record.config_timedate,
            "M_programmed_date": self.record.M_programmed_date,
            "M_programmed_actor": self.record.M_programmed_actor,
            "M_programmed_software": self.record.M_programmed_software,
            "M_programmed_board": self.record.M_programmed_board,
            "M_programmed_functionality": self.record.M_programmed_functionality,
            "M_programmed_configuration": self.record.M_programmed_configuration,
            "C_programmed_date": self.record.C_programmed_date,
            "C_programmed_actor": self.record.C_programmed_actor,
            "C_programmed_software": self.record.C_programmed_software,
            "C_programmed_board": self.record.C_programmed_board,
            "C_programmed_functionality": self.record.C_programmed_functionality,
            "C_programmed_configuration": self.record.C_programmed_configuration,
            "Spare_part": self.record.spare_part,
            "Path": self.record.path
        }