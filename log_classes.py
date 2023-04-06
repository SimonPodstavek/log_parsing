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
        self.Compilation_date = None
        self.Contents = None

    def getBoard(self):
        return self.Board


class RecordBuilder :
    #Create new empty instance of record class
    def __init__(self) -> None:
        self.record = Record()
    def setHDV(self,HDV):
        self.record.HDV = HDV
        return self
    def setPAP_date(self,PAP_date):
        self.record.PAP_date = PAP_date
        return self
    def setPAP_time(self,PAP_time):
        self.record.PAP_time = PAP_time
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
    def setCompilation_date(self,compilation_date):
        self.record.Compilation_date = compilation_date
        return self
    def setContents(self,contents):
        self.record.Contents = contents
        return self
    def build(self):
        return self.record
