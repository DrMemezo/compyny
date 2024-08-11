import random
from errors import *

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
    def __init__(self,rarity:str,id:int) -> None:
        super().__init__(rarity)
        self.id:int = id
        match rarity: # Get a value for the scrap based on the rarity
            # TODO: Take the naming and value of scrap seperate from this function
            
            case 'rare':
                self.value = random.randint(200,250)
                self.name = random.choice(["Block O' Gold","Reactor core","True rolex watch"])
            case 'uncommon':
                self.value =  random.randint(135, 185)
                self.name = random.choice(["Candlestick","Airhorn","Rubiks Cube"])
        
            case 'common':
                self.value = random.randint(50, 100)
                self.name = random.choice(["Fake rolex watch","May/June 2024 Maths paper","disapproving skull"])


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
        self.exit_flag = RetreatFlag # Flag type
        # A dictionary of percentages of scrap appearing
        self._RARITIES = {
            # Each rarity has its own dictionary, for monsters, scraps and default value
            
            "rare": {
                "default": 15,
                "scrap": 15,
                "increment": 2, 
            },
            "uncommon": {
                "default": 35,
                "scrap": 35,
                "increment": 5
            },
            "common": {
                "default": 50,
                "scrap": 50,
                "increment": 10,
            }
        }

        self.events = {
            'scrap' : [],
            'monster': None 
        }
    
    def mod_rarity(self, rarity:str, increment_all:bool=True):
        """Resets a rarity and increases all other rarities IN SCRAPS"""
        rarity_types = list(self._RARITIES.keys())
        if rarity not in rarity_types:
            raise ValueError("unsupported rarity in mod_rarity")
        self._RARITIES[rarity]["scrap"] = self._RARITIES[rarity]["default"]    
         
        if increment_all:
            rarity_types.remove(rarity)
            for rarities in rarity_types:
                self._RARITIES[rarities]["scrap"] += self._RARITIES[rarities]["increment"]

    def get_scraps(self, bound:int=5):
        """Returns a list of event objects"""
        self.events['scrap'] = []
        limit = random.randint(3, bound)
        for id in range(0, limit):
            # Basic percentage
            chance = random.randint(1, 100)
            # Determining rarity of scrap object
            for rarities in ["rare", "uncommon", "common"]:
                if chance < self._RARITIES[rarities]["scrap"]:
                    rarity = rarities
                    break
            
            try:
                self.mod_rarity(rarity=rarity)
                self.events['scrap'].append(Scrap(rarity=rarity, id=id))
            except UnboundLocalError: # No scrap selected
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

