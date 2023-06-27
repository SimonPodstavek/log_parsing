import math

class ziak:
    def __init__(self, meno: str, vyska = None, hmotnost = None) -> None:
        self.meno = meno
        self.vyska = vyska
        self.hmotnost = hmotnost

    def set_height(self, vyska):
        self.vyska = vyska

    def set_weight(self, hmotnost):
        self.hmotnost = hmotnost

    def get_height(self):
        return self.vyska

    def get_weight(self):
        return self.hmotnost
    
    def get_name(self):
        return self.meno

    def get_BMI(self):
        return self.hmotnost / math.pow(self.vyska,2)
        


trieda_2A = [ziak("Patrik Hamrák", 1.70, 50),ziak("Valentina van Veen"),ziak("Šimon Podstavek")]



for person in trieda_2A:
    if person.get_height() == None:
        person.set_height(float(input(f"Zadajte vysku v metroch pre {person.get_name()}: "))) 
    
    if person.get_weight() == None:
        person.set_weight(int(input(f"Zadajte hmotnost v kilogramoch pre {person.get_name()}: "))) 

    print(f"Žiak {person.get_name()} má BMI: {person.get_BMI()}")