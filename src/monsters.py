from src.classes import Event, Ship, Scrap
import src.errors as er
from src.options import styles, wait
import random
from src.roll import roll



class Monster(Event):
    """A Monster is an event which occurs and can damage the player."""
    def __init__(self, rarity:str,name="Monster",description="The Monster Template",
                damage:int=7, health:int=10,
                is_aggresive=False, is_hidden=False,
                is_persistant=False) -> None:
        super().__init__(rarity)
        self.damage = damage
        self.name = name
        self.description = description
        self.aggresive = is_aggresive
        self.hidden = is_hidden
        self.health = health
        self.persistant = is_persistant
        self.set_message()

    def attack(self, ship:Ship,
                crit:int=0,hit:int=100,miss:int=0,
                **kwargs) -> Ship:
        """Try to attack the player. Values for crit, hit and miss must equal to 100"""
        ship.log = ""
        if self.is_dead() or not self.aggresive: # Does not attack if it is dead or not aggresive
            return ship

        result = roll(crit=crit, hit=hit, miss=miss)
        match result:
            case "crit":
                damage = self.damage + ((self.damage * 0.5) // 1)
                ship.health -= damage 
                ship.log += f"\t-- CRITICAL DAMAGE SUSTAINED --\n\tThe {self.name} dealt {damage} damage"
            case "hit":
                damage = self.damage
                ship.health -= damage
                ship.log += f"The {self.name} dealt {damage} damage"
            case "miss":
                ship.log += f"The {self.name} missed its attack" 
     
        if ship.is_dead():
            if kwargs['is_progressing']:
                raise er.ProgressFailFlag("player killed while progressing")
            raise er.KilledFlag("player health is 0")
        
        ship.log += "\n"

        return ship

    def is_dead(self):
        return self.health <= 0
    
    def approach(self, msgs:list[str]=["A monster aprroaches!"]) -> str: 
        """Shows a message when approaching the player"""
        if self.hidden:
            return ""
        return random.choice(msgs)

    def aggrevate(self, msgs:list[str]=[f"The Monster has become aggresive!"]) -> str:
        """Become aggressive if the player has done something"""
        if self.aggresive:
            return ""
        
        self.aggresive = True
        return random.choice(msgs)
    
    def set_message(self, kill:str="The Monster killed the player",
                      progfail:str="Progress failed",
                      custom:str="Custom Killed message") -> None:
        self.MESSAGE = {
            er.KilledFlag: kill,
            er.CustomKilledFlag: custom,
            er.ProgressFailFlag: progfail
        }

    def get_message(self, flag:Exception):
        try:
            return self.MESSAGE[flag]
        except:
            raise ValueError("Unsupported flag entered...")

    def __str__(self) -> str:
        return f"{self.name.title()}"
    
class Lootbugs(Monster):
    def __init__(self, rarity: str, name="Lootbugs", description="A horde of happy horders",
                damage: int = 2, health: int = 5, is_aggresive=False, is_hidden=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden)

    def set_message(self, 
                    kill: str = "The Lootbugs bit, and tore at your head until they reached the skull...", 
                    progfail: str = "You tried leaving with what you had, but the lootbugs had other plans...", 
                    custom: str = "Custom Killed message") -> None:
        return super().set_message(kill, progfail, custom)
    
    def approach(self,
    msgs: list[str] = ["A horde of lootbugs aprroaches!",
                       "The buzzing and fuzzing of a mob of Lootbugs echos throughout the room"]) -> str:
        return super().approach(msgs)

    def attack(self, ship: Ship, 
               crit: int = 0, hit: int = 65, miss: int = 35,
               **kwargs) -> Ship:
        ship: Ship = super().attack(ship, crit, hit, miss, **kwargs)
        
        return ship
    
    def aggrevate(self, 
                  msgs: list[str] = ["The Lootbugs are angry!",
                                    "The Horde of lootbugs fill with rage","The lootbugs are now standing on their legs and hissing... Yipee?"]) -> str:
        return super().aggrevate(msgs)

class Bracken(Monster):

    def __init__(self, rarity: str, name="Bracken", description="A leavy maroon marauder", damage: int = 7, health: int = 6,
                is_aggresive=False, is_hidden=True,
                is_persistant=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.moves = 0
        self.stare_counter = 1
    
    def set_message(self, kill: str = "The Bracken slashed and slashed, until you dropped dead...",
                    progfail: str = "The Bracken took the oppurtunity while you were progressing",
                    custom: str = "Suddenly, you felt your neck twist and creak... until it snapped.") -> None:
        return super().set_message(kill=kill, progfail=progfail, custom=custom)

    def attack(self, ship: Ship, crit: int = 20, hit: int = 50, miss: int = 30, **kwargs) -> Ship:
        # A Bracken will kill the player in 3 moves if not stared at...
        self.moves += 1
        # Every 2 moves, the stare counter decreases. if it reaches zero, the bracken kills the player
        if self.moves % 2 == 0:
            self.stare_counter -=1

        if self.stare_counter == 0:
            raise er.CustomKilledFlag
            
        # However, if the player stares at the bracken for too long, it will be aggresive
        if self.aggresive:
            return super().attack(ship, crit=crit, hit=hit, miss=miss, **kwargs)
        
        return ship

    def aggrevate(self, msgs: list[str] = 
                  ["The Bracken's eyes have turned red..."]) -> str:
        return super().aggrevate(msgs)    

    def alert_response(self) -> str:
        """If the player uses alert, it shows them that a bracken is here and 
        prolongs their demise, however, if the bracken is stared at too long, it becomes aggresive..."""
       
        message = ""
        if self.aggresive:
            return message #Braken is already aggresive
 
        self.stare_counter += 1

        if self.stare_counter == 4:
            message = self.aggrevate()

        if self.hidden:
            message = "You found a bracken sulking in the shadows..."
            self.hidden = False
        elif not self.aggresive:
            message = random.choice(["You hear the Bracken snarling...",
                                     "You and the Bracken feel the tension rising...",
                                     "The Bracken creeps closer"])
        
        return message

class Jester(Monster):
    def __init__(self, rarity: str, name="Jester", description="An ominous box with legs", damage: int = 100, health: int = 1000,
                  is_aggresive=False, is_hidden=False, is_persistant=True) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.moves = 0 # How many rooms the ship has travelled since it was winding
        self.catch = 0 # Counts the moves the Jester has made after being aggravated
    
    def attack(self, ship: Ship,
                crit: int = 0, hit: int = 100, miss: int = 0, **kwargs) -> Ship:

        return ship
        return super().attack(ship, crit, hit, miss, **kwargs)

# -- MONSTER RELATED FUNCTIONS --
def attack(**kwargs) -> Ship:
    ship:Ship = kwargs["ship"]
    monster:Monster = ship.events['monster']

    if not monster:
        ship.log += "You swing and swing and swing... but there is nothing there"
        return ship
        
    if monster.hidden:
        ship.log += "You swing to the sounds of shuffling and scraping, but you do not hit anything..."
        return ship

    
    if monster.is_dead():
        ship.log = random.choice([f"You swung at the corpse of the dead {str(monster)}",
                                  f"The {str(monster)} cannot hurt you anymore, captain.",
                                  f"Dear God! It's already dead!"])
        return ship

    ship.log += monster.aggrevate()
     
    # TODO: Instead of hardcoding these values, use values from the weapon the ship has
    result = roll(miss=5, crit=20, hit=75)
    match result:
        case "miss":   
            ship.log += random.choice(["You missed!",
                                        "A swing and a miss!",
                                        "You missed. happens to the best of us."])
        case "crit":
            monster.health -= (ship.damage * 1.5) // 1
            ship.log = "\t -- CRITICAL HIT --"
            ship.log += f"\nYou dealt {(ship.damage * 1.5) // 1} damage to the {str(monster)}. {random.choice(["Nice!", "Bravo!", "Magnificent!"])}"
        case "hit":
            monster.health -= ship.damage
            ship.log += f"\nYou dealt {ship.damage} damage to the monster."
    
    if monster.is_dead():
        ship.log += f"\nThe {str(monster)} has been slained..."
    
    ship.events['monster'] = monster
    return ship 
 

def alert(**kwargs) -> Ship:
    ship = kwargs['ship']
    monster = ship.events['monster']
    ship.log = ""
    if monster is None: # No monster selected
        ship.log += "\n"
        ship.log += random.choice(["You swear you saw something in the corner of your eye...",
                                "Must've been the wind...",
                                "Your eyes darted across the room, yet you discovered no threat"])
        return ship
    

    
    try:
        ship.log = monster.alert_response()
    except AttributeError: # This monster does not have a custom alert response
        pass 
        
    ship.log += f"\n{monster.name.upper()}\n\t{monster.description}\n"
    ship.log += "STATUS: "
    if monster.is_dead():
        ship.log += "DEAD"
    else:
        ship.log += f"ALIVE -- HP: {monster.health}"
        ship.log += f"\n\t DAMAGE: {monster.damage}"
        ship.log += f"\n\t AGGRESIVE? {monster.aggresive}"

    return ship


def think(**kwargs) -> Ship:
    ship = kwargs['ship']
    try:
        is_hidden = ship.events['monster'].hidden
    except AttributeError: # No monster
        is_hidden = True
    
    message = f"'alert': Be alerted of all the threats inside the room.\n"
    if not is_hidden:
        message += f"'attack': Chance to deal {ship.damage} damage.\n"
        message += f"'run': Drop everything and run!"
    ship.log = message 
    return ship

def run(**kwargs):
    # Raise Run flag
    raise er.RunFlag

def progress(**kwargs):
    ship:Ship = kwargs['ship']
    monster:Monster = ship.events['monster']

    # TODO:If monster is alive, it will crit the player as it leaves.
    try: 
        ship = monster.attack(ship, crit=100, hit=0, miss=0, is_progressing=True)
    except AttributeError: # No monster 
        pass
    
    ship.events['monster'] = None # Resetting monster
    
    try:
        ship.progress()
    except TypeError:
        pass
    ship.get_scraps() # Gets a list of events

    ship.log += "\n" + random.choice(["Walking through the maze of endless hallways, you find the next room.",
                             "You feel a cold chill up your spine as you walk into the next room",
                             "You hear sounds and scrapes in the distance as you walk into the next room",
                             "Your flashlight flickers in the ominous darkness, yet you find your way to the next room."])
    return ship 

def collect(**kwargs):
    ship = kwargs['ship']
    if isinstance(ship.events['monster'], Lootbugs):
        ship.log = ship.events['monster'].aggrevate()
    
    return ship

M_OPTIONS = {
    'attack': attack,
    'alert': alert,
    'think': think,
    'run': run,
    'progress': progress,
    'collect': collect 
}

styles.update({
    'attack' : "medium_violet_red",
    'run': "bold bright_red",
    'alert': "dark_orange3"
})

wait.update({
    'attack': 0.09,
    'run': 0.1,
    'alert': 0.05
})


GET_MONSTER = {
    "rare": [Monster],
    "uncommon": [Bracken],
    "common": [Lootbugs]
}

PROBABILITIES = {
    "rare" : 5,
    "uncommon" : 15,
    "common": 35,
    "nothing": 45
}

def get_monster() -> Monster:
    global PROBABILITIES
    # Roll a dice
    result = roll(**PROBABILITIES)
    
    #TODO: Make rare and uncommon progressively more apparent.

    if result == "nothing":
        raise er.NoMonsterFlag
    
    
    return random.choice(GET_MONSTER[result])(rarity=result) # Gets a random monster