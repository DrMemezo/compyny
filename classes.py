import random
from errors import *

class Event:
    """Event occurs when the player progresses to another room
        They have a rarity type, and the probability of an event occuring is linked to that type"""

    def __init__(self, rarity:str) -> None:
        if rarity not in ["common", "uncommon", "rare"]:
            raise ValueError("unsupported rarity")
        self.rarity = rarity

    def is_hidden(self) -> bool:
        return self.hidden
    
    def show(self):
        self.hidden = False

class Scrap(Event):
    """Scraps are basically an event which occurs when a user walks into a new room
    They have a monetary value based on their rarity type"""
    def __init__(self,rarity:str,id:int) -> None:
        super().__init__(rarity)
        self.hidden:bool = random.choice([True, False])
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
    def __init__(self, name:str="Johnathan doe") -> None:
        self.health = 3 
        self.points = 0 # Points determined by scraps
        self.current_scrap = None # Current scrap stored before progressing to the next room
        self.name = name 
        self.log:str = ""
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
    
    #TODO: Make this better
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

    def get_events(self, bound:int=5):
        """Returns a list of event objects"""
        self.events = {
            'scrap' : []
        }
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


def inspect(**kwargs) -> str:
    message = "There is nothing to inspect"
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    event_values = []
    for event in events:
        if type(event) is Scrap and not event.is_hidden():
            event_values.append(f"{event.name.title()}, (id: '{event.id}') has a value of {event.value}\n")
    
    if event_values:
        message = "".join(event_values)
    
    ship.log = message
    return ship

def find(**kwargs) -> str:
    message = ""
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    for event in events:
        try:
            if event.is_hidden() and isinstance(event, Scrap):
                event.show()
                message += f"You Found a {event.name}, *{event.id}*\n"
        except:
            pass
    if not message:
        message = "Nothing of value was found..."

    ship.log = message
    return ship

def think(**kwargs) -> str:
    message = "You think long and hard about what to do next...\n"
    message += "'find': Find and locate any hidden items (or dangers) in this room\n"
    message += "'inspect': Inspect scrap that you've already found\n"
    message += "'progress': Progress to the next room\n"
    message += "'collect {id}': Add scraps to your collection\n"
    message += "'overview: Get an overview for your ship\n"
    message += "'retreat': Call it a day and get outa town\n"

    ship = kwargs['ship']
    ship.log = message
    return ship

def find_from_id(scrap_events:list[Scrap], id:int) -> Scrap:
    for scrap in scrap_events:
        if scrap.id == id:
            return scrap
    return None

def collect(**kwargs) -> str:
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    message = random.choice(["That is not a valid Id...", 
                        "No time for mistakes, captain. Look at the id.",
                        "What are you trying to collect, captain"])     
    try:
        collect_id = int(kwargs['subject'])
    except TypeError:
        # No ID given
        message = random.choice(["No scrap was specified...",
                                "You tried collecting the air. It didnt work.",
                                "What are you trying to collect, captain?"])
    except ValueError:
        # Incorrect Id given
        pass
    else:
    # Trying to find if collect is in events
        if collect_scrap := find_from_id(events, collect_id): # If id is of a valid scrap
            try:
                if ship.current_scrap.id == collect_id: # Already collected
                    message = "You have already collected this item\t...perhaps it was the wrong id?"
                else: # Different Id
                    message = f"Switched out {ship.current_scrap.name}({ship.current_scrap.value}) for {collect_scrap.name}({collect_scrap.value})"
            except AttributeError: # No scrap currently stored
                message = f"Collected {collect_scrap.name.title()} for {collect_scrap.value}"
            finally:
                ship.current_scrap = collect_scrap
                
    ship.log = message
    return ship             

def progress(**kwargs):
    ship:Ship = kwargs['ship']
    try:
        ship.progress()
    except TypeError:
        pass
    ship.get_events() # Gets a list of events

    ship.log = random.choice(["Walking through the maze of endless hallways, you find the next room.",
                             "You feel a cold chill up your spine as you walk into the next room",
                             "You hear sounds and scrapes in the distance as you walk into the next room",
                             "Your flashlight flickers in the ominous darkness, yet you find your way to the next room."])
    return ship 

def overview(**kwargs):
    """Gives an overview of the ship at the current moment of function call"""
    ship:Ship = kwargs['ship']
    message = "SHIP STATUS---\n"
    message += f"SHIP HEALTH: {ship.health}\n"
    message += f"SHIP POINTS: {ship.points}\n"
    message += f"CURRENT SCRAP: "
    try:
        message += f"{ship.current_scrap.name}\n"
        message += f"\tPOINTS: {ship.current_scrap.value}\n"
        message += f"\tRARITY: {ship.current_scrap.rarity.title()}"
    except AttributeError: # No scrap selected
        message += "UNSELECTED"
    
    ship.log = message
    return ship
        
def retreat(**kwargs):
    raise RetreatFlag

OPTIONS = {
    'inspect' : inspect,
    'find' : find,
    'think' : think,
    'collect': collect,
    'progress': progress,
    'overview': overview,
    'retreat': retreat
}

# Stores the style for each action
styles = {
    "default" : "bold white on blue",
    "danger" : "bold white on red",
    "inspect": "sea_green1",
    "find": "light_slate_blue",
    "think": "bold spring_green3 on white",
    "advise": "grey50",
    "advise_bold": "bold underline grey50",
    "collect": "light_goldenrod1",
    "progress": "bold bright_cyan",
    "overview": "turquoise2"
}

# Stores the interval for slow printing for each action
wait = {
    "think": 0.001,
    "advise": 0.02,
    "find": 0.03,
    "inspect": 0.03,
    "overview": 0.025,
    "collect": 0.03,
    "progress": 0.05
}
