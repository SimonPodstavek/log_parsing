class SafebyteLocations:
    def __init__(self, HDV: slice, actor: slice, board: slice, software_version: slice, software_label: slice, checksum_Flash: slice, checksum_EEPROM: slice) -> None:
        self.HDV = HDV
        self.actor = actor
        self.board = board
        self.software_version = software_version
        self.software_label = software_label
        self.checksum_Flash = checksum_Flash
        self.checksum_EEPROM = checksum_EEPROM
    
    def get_HDV(self):
        return self.HDV
    
    def get_actor(self):
        return self.actor
    
    def get_board(self):
        return self.board
    
    def get_software_version(self):
        return self.software_version

    def get_software_label(self):
        return self.software_label
    
    def get_checksum_Flash(self):
        return self.checksum_Flash
    
    def get_checksum_EEPROM(self):
        return self.checksum_EEPROM
    
version_by_offset = {3: [2], 2:[496, ]}

safebyte_locations = {
    2 : {
        1 : SafebyteLocations(HDV = slice(6,3,-1), actor = slice(7,8), board = slice(2,4), software_version = slice(15,16), software_label = slice(13,15), checksum_Flash = slice(0,1), checksum_EEPROM = slice(1,2)),
        2 : SafebyteLocations(HDV = None, actor = slice(8,10), board = slice(2,5), software_version = slice(15,16), software_label = slice(13,15), checksum_Flash = slice(0,1), checksum_EEPROM = slice(1,2))
        },

    3 : {
        1 : SafebyteLocations(HDV = None, actor = slice(3,5), board = slice(8,10), software_version = slice(15,16), software_label = slice(11,15), checksum_Flash = slice(1,2), checksum_EEPROM = slice(2,3)),
        2 : SafebyteLocations(HDV = None, actor = slice(3,5), board = slice(8,11), software_version = slice(15,16), software_label = slice(11,15), checksum_Flash = slice(1,2), checksum_EEPROM = slice(2,3)),
        3 : SafebyteLocations(HDV = None, actor = slice(3,5), board = slice(8,11), software_version = slice(15,16), software_label = slice(11,15), checksum_Flash = slice(1,2), checksum_EEPROM = slice(2,3)),
    
    }
}

safebyte_versions = {
    1:1,
    254:1,
    2:2,
    3:3,
    4:3
}

