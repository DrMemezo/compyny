import random
from src.errors import *
from src.roll import roll
from pathlib import Path
import csv

PATHS = {
    "rare": Path("assets/scraps/rare.csv"),
    "uncommon": Path("assets/scraps/uncommon.csv"),
    "common": Path("assets/scraps/common.csv"),
    "weapon": Path("assets/scraps/weapons.csv")
}

for path in PATHS.values():
    if not path.exists():
        raise FileNotFoundError

def get_scrap_from(rarity):
        """Gets the name, description (and damage from weapons)
        for scraps"""
        csv.rea


class Event:
    """Event occurs when the player progresses to another room
        They have a rarity type, and the probability of an event occuring is linked to that type"""

    def __init__(self, rarity:str) -> None:
        if rarity not in ["common", "uncommon", "rare"]:
            raise ValueError("unsupported rarity")
        self.rarity = rarity
        self.hidden:bool = random.choice([True, False])

    def is_hidden(self) -> bool:
        return self.hidden
    
    def show(self):
        self.hidden = False

class Scrap(Event):
    """Scraps are basically an event which occurs when a user walks into a new room
    They have a monetary value based on their rarity type"""
    def __init__(self,rarity:str,id:int,name:str="Scrap",
                 description:str="Generic Scrap",
                 value:int=50) -> None:
        super().__init__(rarity)
        self.id = id
        self.description = description
        self.name = name
        self.value = value
            

    def __str__(self) -> str:
        return random.choice([
            f"Despite the overwhelming darkness... you find a {self.name}",
            f"A {self.name} blocks your path...",
            f"How peculiar... a {self.name} lies in front of you...",
            f"You were so distracted by the blood on the wall... you didn't even realise the {self.name}",
            f"You stumbled over a {self.name}, How clumsy!",
            f"In the corner of your eye, you spotted a {self.name}"
        ])

class Ship:
    def __init__(self, name:str="Johnathan doe",health:int=10) -> None:
        self.health = health 
        self.points = 0 # Points determined by scraps
        self.current_scrap = None # Current scrap stored before progressing to the next room
        self.name = name 
        self.log:str = ""
        self.damage = 3
        self.chances:dict[int] = {
            "crit": 20,
            "hit": 70,
            "miss": 10
        }
        self.exit_flag = RetreatFlag # Flag type
        self.insanity:int = 0 # The more insane the player gets, the rarer the monsters 

        self.events = {
            'scrap' : [],
            'monster': None 
        }
    
    def get_scraps(self):
        """Returns a list of event objects"""
        self.events['scrap'] = []
        limit = random.randint(3, 5)
        for id in range(0, limit):
            # Basic percentage
            result:str = roll(common=50, uncommon=25, rare=5, nothing=20)
            
            match result:
                case "nothing":
                    continue

            try:
                self.events['scrap'].append(Scrap(rarity=result, id=id))
            except TypeError: # No scrap selected
                continue


    def collect(self, scrap:Scrap):
        if not isinstance(scrap, Scrap):
            raise TypeError("Tried to collect a non-scrap item")
        
        self.points += scrap.value
        
    def progress(self):
        """Add scrap the total value, also modify rarities for monsters"""
        self.collect(self.current_scrap)
        self.current_scrap = None
    
    def is_dead(self):
        return self.health <= 0 

