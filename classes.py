import random



class Event:
    """Event occurs when the player progresses to another room
        They have a rarity type, and the probability of an event occuring is linked to that type"""

    def __init__(self, rarity:str) -> None:
        if rarity not in ["common", "uncommon", "rare"]:
            raise ValueError("unsupported rarity")
        self.hidden:bool = random.choice([True, False])

    def is_hidden(self) -> bool:
        return self.hidden
    
    def show(self):
        self.hidden = False

    def option(self, action:str):
        """Calls a function based on the action performed by the user"""
        pass

class Scrap(Event):
    """Scraps are basically an event which occurs when a user walks into a new room
    They have a monetary value based on their rarity type"""
    def __init__(self,rarity:str) -> None:
        super().__init__(rarity)
        match rarity: # Get a value for the scrap based on the rarity
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
    
    def unique_event():
        """If any scrap is unique from the rest, they can use this module"""
        pass

class Ship:
    def __init__(self, name:str="Johnathan doe") -> None:
        self.health = 3
        self.points = 0
        self.scraps = {}
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

    def get_events(self, bound:int=3):
        """Returns a list of event objects"""
        self.events = []
        limit = random.randint(1, bound)
        for _ in range(0, limit):
            # Basic percentage
            chance = random.randint(1, 100)
            # Determining rarity of scrap object
            if chance < self._RARITIES["rare"]["scrap"]:
                rarity = "rare"
            elif chance < self._RARITIES["uncommon"]["scrap"]:
                rarity = "uncommon"
            elif chance < self._RARITIES["common"]["scrap"]:
                rarity = "common"
            else:
                continue # No scrap selected
            self.mod_rarity(rarity=rarity)
            self.events.append(Scrap(rarity=rarity))
        
    def collect(self, scrap:Scrap):
        if not isinstance(scrap, Scrap):
            raise TypeError("Tried to collect a non-scrap item")
        
        self.points += scrap.value
        # Keep a log of all scraps
        try:
            self.scraps[scrap.name] += 1
        except KeyError:
            self.scraps[scrap.name] = 1


def inspect(**kwargs) -> str:
    message = "There is nothing to inspect"
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    event_values = []
    for event in events:
        if type(event) is Scrap and not event.is_hidden():
            event_values.append(f"{event.name.title()} has a value of {event.value}\n")
    
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
                message += f"You Found a {event.name}\n"
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
    message += "'collect': Add scraps to your collection\n"

    ship = kwargs['ship']
    ship.log = message
    return ship

def collect(**kwargs) -> str:
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    message = "There was nothing to collect..."

    collection = []
    for event in events:
        if not event.is_hidden() and isinstance(event, Scrap):
            ship.collect(event)
            collection.append(f"You collected {event.name} for {event.value}\n")

    if collection:
        message = "".join(collection)

    ship.log = message
    return ship             


OPTIONS = {
    'inspect' : inspect,
    'find' : find,
    'think' : think,
    'collect': collect
}

# Stores the style for each action
styles = {
    "default" : "bold white on blue",
    "danger" : "bold white on red",
    "info": "turquoise2",
    "inspect": "sea_green1",
    "find": "light_slate_blue",
    "think": "bold spring_green3 on white",
    "advise": "grey50",
    "collect": "light_goldenrod1"
}

# Stores the interval for slow printing for each action
wait = {
    "think": 0.001,
    "advise": 0.02,
    "find": 0.03,
    "inspect": 0.05,
    "overview": 0.025,
    "collect": 0.03
}
