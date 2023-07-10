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
        self.datetime = None
        self.actor = None
        self.board = None
        self.software = None
        self.checksum_Flash = None
        self.checksum_EEPROM = None
        self.compilation_date = None
        self.path = None
        self.content = None

#Record class is a template for KAMRecordBuilder
class KAMRecord:
    def __init__(self) -> None:
        self.HDV = None
        self.config_datetime = None
        self.M_programmed_date = None
        self.M_programmed_actor = None
        self.M_programmed_software = None
        self.M_programmed_board = None
        self.M_actor = None
        self.M_functionality = None
        self.M_configuration = None
        self.M_wheel_diameter = None
        self.M_IRC = None
        self.M_spare_part = None
        self.C_programmed_date = None
        self.C_programmed_actor = None
        self.C_programmed_software = None
        self.C_programmed_board = None
        self.C_actor = None
        self.C_functionality = None
        self.C_configuration = None
        self.C_wheel_diameter = None
        self.C_IRC = None
        self.C_spare_part = None
        self.path = None
        self.content = None

#New empty instance of PAP record class
class PAPRecordBuilder :
    def __init__(self) -> None:
        self.record = PAPRecord()
    def set_HDV(self,HDV):
        self.record.HDV = HDV
        return self
    def set_datetime(self,datetime):
        self.record.datetime = datetime
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
    def set_compilation_date(self,compilation_date):
        self.record.compilation_date = compilation_date
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
    def get_datetime(self):
        return self.record.datetime
    def get_actor(self):
        return self.record.actor    
    def get_board(self):
        return self.record.board
    def get_software(self):
        return self.record.software
    def get_checksum_Flash(self):
        return self.record.checksum_Flash 
    def get_checksum_EEPROM(self):
        return self.record.checksum_EEPROM 
    def get_compilation_date(self):
        return self.record.compilation_date
    def get_content(self):
        return self.record.content
    def get_path(self):
        return self.record.path  
    def build(self):
        return self.record
    


    # def to_dict(self):
    #     return {
    #         "date": self.record.datetime,
    #         "Actor": self.record.actor,
    #         "Board": self.record.Board,
    #         "Software": self.record.Software,
    #         "Checksum_Flash": self.record.Checksum_Flash,
    #         "Checksum_EEPROM": self.record.Checksum_EEPROM,
    #         "Compilation_datetime": self.record.Compilation_datetime,
    #         "Path": self.record.path
    #     }
    

#New empty instance of KAM record class
class KAMRecordBuilder :
    def __init__(self) -> None:
        self.record = KAMRecord()
    def set_HDV(self,HDV):
        self.record.HDV = HDV
        return self
    def set_config_datetime(self,config_datetime):
        self.record.config_datetime = config_datetime
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
    def set_M_actor(self,M_actor):
        self.record.M_actor = M_actor
        return self
    def set_M_functionality(self,M_functionality):
        self.record.M_functionality = M_functionality
        return self
    def set_M_configuration(self,M_configuration):
        self.record.M_configuration = M_configuration
        return self
    def set_M_wheel_diameter(self,C_wheel_diameter):
        self.record.C_wheel_diameter = C_wheel_diameter
        return self
    def set_M_IRC(self,M_IRC):
        self.record.M_IRC = M_IRC
        return self
    def set_M_spare_part(self,M_spare_part):
        self.record.M_spare_part = M_spare_part
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
    def set_C_actor(self,C_actor):
        self.record.C_actor = C_actor
        return self
    def set_C_functionality(self,C_functionality):
        self.record.C_functionality = C_functionality
        return self
    def set_C_configuration(self,C_configuration):
        self.record.C_configuration = C_configuration
        return self
    def set_C_wheel_diameter(self,C_wheel_diameter):
        self.record.C_wheel_diameter = C_wheel_diameter
        return self
    def set_C_IRC(self,C_IRC):
        self.record.C_IRC = C_IRC
        return self
    def set_C_spare_part(self,C_spare_part):
        self.record.C_spare_part = C_spare_part
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
    def get_config_datetime(self):
        return self.record.config_datetime
    def get_M_programmed_date(self):
        return self.record.M_programmed_date
    def get_M_programmed_actor(self):
        return self.record.M_programmed_actor
    def get_M_programmed_software(self):
        return self.record.M_programmed_software
    def get_M_programmed_board(self):
        return self.record.M_programmed_board
    def get_M_actor(self):
        return self.record.M_actor
    def get_M_functionality(self):
        return self.record.M_functionality
    def get_M_configuration(self):
        return self.record.M_configuration
    def get_M_wheel_diameter(self):
        return self.record.M_wheel_diameter
    def get_M_IRC(self):
        return self.record.M_IRC
    def get_M_spare_part(self):
        return self.record.M_spare_part
    def get_C_programmed_date(self):
        return self.record.C_programmed_date
    def get_C_programmed_actor(self):
        return self.record.C_programmed_actor
    def get_C_programmed_software(self):
        return self.record.C_programmed_software
    def get_C_programmed_board(self):
        return self.record.C_programmed_board
    def get_C_actor(self):
        return self.record.C_actor
    def get_C_functionality(self):
        return self.record.C_functionality
    def get_C_configuration(self):
        return self.record.C_configuration
    def get_C_wheel_diameter(self):
        return self.record.C_wheel_diameter
    def get_C_IRC(self):
        return self.record.C_IRC
    def get_C_spare_part(self):
        return self.record.C_spare_part
    def get_content(self):
        return self.record.content
    def get_path(self):
        return self.record.path  
    
    def build(self):
        return self.record
    def KAM_to_dict(self):
        return {
            "HDV": self.record.HDV,
            "Config_datetime": self.record.config_datetime,
            "M_programmed_date": self.record.M_programmed_date,
            "M_programmed_actor": self.record.M_programmed_actor,
            "M_programmed_software": self.record.M_programmed_software,
            "M_programmed_board": self.record.M_programmed_board,
            "M_actor": self.record.M_actor,
            "M_functionality": self.record.M_functionality,
            "M_configuration": self.record.M_configuration,
            "M_spare_part": self.record.M_spare_part,
            "C_programmed_date": self.record.C_programmed_date,
            "C_programmed_actor": self.record.C_programmed_actor,
            "C_programmed_software": self.record.C_programmed_software,
            "C_programmed_board": self.record.C_programmed_board,
            "C_actor": self.record.C_actor,
            "C_functionality": self.record.C_functionality,
            "C_configuration": self.record.C_configuration,
            "C_spare_part": self.record.C_spare_part,
            "Path": self.record.path
        }