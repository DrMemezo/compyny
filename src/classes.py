import random


try:
    from errors import *
    from roll import *
    from utils import PATHS
except ModuleNotFoundError:
    from src.errors import *
    from src.roll import *
    from src.utils import PATHS

from pathlib import Path
import csv


for path in PATHS.values():
    if not path.exists():
        raise FileNotFoundError

def get_conts_from(path:Path):
        """Gets the contents from the file paths..."""
        with open(path) as file:
            contents = list(csv.reader(file,delimiter='|', skipinitialspace=True))

        return contents

CONTENTS = {name:get_conts_from(path) for (name, path) in PATHS.items()}
VAL_RANGE = {
    "rare": [150,300],
    "uncommon": [100,150],
    "common": [50,100],
    "weapon": [150,200]
}


class Event:
    """Event occurs when the player progresses to another room
        They have a rarity type, and the probability of an event occuring is linked to that type"""

    def __init__(self, rarity:str) -> None:
        self.rarity = rarity

    def is_hidden(self) -> bool:
        return self.hidden
    
    def show(self):
        self.hidden = False

class Scrap(Event):
    """Scraps are basically an event which occurs when a user walks into a new room
    They have a monetary value based on their rarity type"""
    def __init__(self,rarity:str,id:int,name:str="Scrap",
                 description:str="Generic Scrap", is_hidden:bool= False,
                 value:int=50) -> None:
        super().__init__(rarity)
        self.hidden = is_hidden
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

    @staticmethod
    def get_from(rarity:str, id:int, concealed:None|bool=None):
            """Gets the name, description (and damage from weapons)
            for scraps"""
            try:
                scrap_info:list = random.choice(CONTENTS[rarity])
            except KeyError:
                raise ValueError(f"Unsupported Rarity; Recieved: {rarity}")
            
            name:str = scrap_info[0]
            desc:str = scrap_info[1]
            is_hidden:bool =  concealed if concealed else random.choice([True, False])
            value:int = random.randint(*VAL_RANGE[rarity])
            try:
                damage:int = int(scrap_info[2])
                # In the CSV file, this is stored as crit-hit-miss
                stats_raw:str= list(map(int, scrap_info[3].split('-')))
                stats = {
                    "crit": stats_raw[0],
                    "hit": stats_raw[1],
                    "miss": stats_raw[2]
                }
            except IndexError: # Not a Weapon
                pass
            else:
                
                return Weapon("weapon", id=id, damage=damage, stats=stats,
                                name=name,
                                description=desc,
                                value=value)

            return Scrap(rarity, id, 
                         name=name,
                         is_hidden=is_hidden,
                        description=desc,value=value) 

class Weapon(Scrap):
    """Much like Scraps, it has a monetary value and can be collected. However, they boost damage of the player"""
    def __init__(self, rarity: str, stats:dict[str,int|float], id: int, is_hidden:bool=False, name: str = "Scrap", description: str = "Generic Scrap", value: int = 50,
                 damage:int=3, uses:None|int=None) -> None:
        super().__init__(rarity, id, name, description,is_hidden, value)
        self.damage = damage
        self.uses = uses if uses else random.randint(2, 7)
        self.chance:Chance = Chance(**stats)

class Ship:
    """This is the object representing the player. It holds all the stats it needs to"""
    def __init__(self, name:str="Johnathan doe",health:int=10) -> None:
        self.health = health 
        self.points = 0 # Points determined by scraps
        self.name = name 
        
        self.current_scrap:Scrap = None # Current scrap stored before progressing to the next room
        self.current_weapon:Weapon = Weapon("weapon", id=99, damage=3, stats={"crit":20,"hit":75,"miss":5},
                                    name="Company Issued Batons",
                                     description="They look threatening, but are actually made out of cardboard to save money",
                                     value=0, uses=2)
        
        self.log:str = ""
        self.scrap_chance:Chance = Chance(common=20, uncommon=25, rare=5, weapon=15, nothing=35)
        self.monster_chance:Chance = Chance(rare=0, uncommon=15, common=35, nothing=40, hallucination=10)

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
            result:str = self.scrap_chance.roll()
            
            if result == "nothing":
                continue
            if result == "rare":
                self.scrap_chance.add_to(rare=5)
            else:
                self.scrap_chance.reset("rare")

            self.events['scrap'].append(
                Scrap.get_from(result, id)
            )

    def collect(self, scrap:Scrap|Weapon):
        if not isinstance(scrap, Scrap):
            raise TypeError("Tried to collect a non-scrap item")
        
        self.points += scrap.value
        
    def progress(self):
        """Add scrap the total value, also modify rarities for monsters"""
        self.collect(self.current_scrap)
        self.current_scrap = None
        self.monster_chance.add_to(rare=(self.insanity * 0.2), hallucination=(self.insanity * 0.5))
        self.current_weapon.id = 99 # To ensure it has a unique id before progressing.
    
    def is_dead(self):
        return self.health <= 0 

