from classes import Event, Ship, Scrap
import errors as er
from options import styles, wait
import random
from roll import roll



class Monster(Event):
    """A Monster is an event which occurs and can damage the player."""
    def __init__(self, rarity:str,name="Monster",description="The Monster Template",
                damage:int=7, health:int=10,
                is_aggresive=False, is_hidden=False) -> None:
        super().__init__(rarity)
        self.damage = damage
        self.name = name
        self.description = description
        self.aggresive = is_aggresive
        self.hidden = is_hidden
        self.health = health

    def attack(self, ship:Ship,
                crit:int=100,hit:int=0,miss:int=0,
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
                ship.log += f"--CRITICAL--\nThe {self.name} dealt {damage} damage"
            case "hit":
                damage = self.damage
                ship.health -= damage
                ship.log += f"The {self.name} dealt {damage} damage"
            case "miss":
                ship.log += f"The {self.name} missed its attack" 
     
        if ship.is_dead():
            raise er.KilledFlag("player health is 0")

        return ship

    def is_dead(self):
        return self.health <= 0
    
    def approach(self, ship:Ship):
        """Approaching the player"""
        ship.log = f"A monster approaches!"
        return ship

    def aggrevate(self) -> str:
        """Become aggressive if the player has done something"""
        self.aggresive = True
        return f"The {str(self)} has become aggresive!"
    
    def get_message(self, flag:Exception):
        match flag:
            case er.KilledFlag:
                return f"The {str(self)} killed the player in combat"
            case er.ProgressFailFlag:
                return f"The {str(self)} killed the player when retreating"       

    def __str__(self) -> str:
        return f"{self.name.title()}"

    
class Lootbugs(Monster):
    def __init__(self, rarity: str, name="Lootbugs", description="A horde of happy horders",
                damage: int = 1, health: int = 5, is_aggresive=False, is_hidden=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden)
    
    def approach(self, ship: Ship):
        ship.log = "A mob of Lootbugs appears!"
        return ship

    def attack(self, ship: Ship, 
               crit: int = 0, hit: int = 20, miss: int = 80,
               **kwargs) -> Ship:
        ship: Ship = super().attack(ship, crit, hit, miss)
        
        return ship


def attack(**kwargs) -> Ship:
    ship:Ship = kwargs["ship"]
    monster:Monster = ship.events['monster']

    if not monster:
        return ship
        
    if monster.hidden:
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
            monster.health -= ship.damage * 1.5
            ship.log = "\t -- CRITICAL HIT --"
            ship.log += f"\nYou dealt {ship.damage * 1.5} damage to the {str(monster)}. {random.choice(["Nice!", "Bravo!", "Magnificent!"])}"
        case "hit":
            monster.health -= ship.damage
            ship.log += f"\nYou dealt {ship.damage} damage to the monster."
    
    if monster.is_dead():
        ship.log += f"\nThe {str(monster)} has been slained..."
    
    ship.events['monster'] = monster
    return ship 
 

def alert(**kwargs):
    ship = kwargs['ship']
    monster = ship.events['monster']
    ship.log = ""
    if monster is None: # No monster selected
        ship.log = random.choice(["You swear you saw something in the corner of your eye...",
                                "Must've been the wind...",
                                "Your eyes darted across the room, yet you discovered no threat"])
        return ship
    

    if monster.hidden:
        try:
            monster.alert_response()
        except AttributeError: # This monster does not have a custom alert response
            pass 
        
        ship.log += "You spotted a monster!\n"
    ship.log += f"{monster.name.upper()}\n\t{monster.description}\n"
    ship.log += "STATUS: "
    if monster.is_dead():
        ship.log += "DEAD"
    else:
        ship.log += f"ALIVE -- HP: {monster.health}"
        ship.log += f"\n\t DAMAGE: {monster.damage}"
        ship.log += f"\n\t AGGRESIVE? {monster.aggresive}"

    return ship


def think(**kwargs):
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
    ship = kwargs['ship']
    monster = ship.events['monster'] 

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
    
    try:
        ship.progress()
    except TypeError:
        pass
    ship.get_scraps() # Gets a list of events

    ship.log = random.choice(["Walking through the maze of endless hallways, you find the next room.",
                             "You feel a cold chill up your spine as you walk into the next room",
                             "You hear sounds and scrapes in the distance as you walk into the next room",
                             "Your flashlight flickers in the ominous darkness, yet you find your way to the next room."])
    return ship 

def collect(**kwargs):
    ship = kwargs['ship']
    if isinstance(ship.events['monster'], Lootbugs):
        ship.events['monster'].aggrevate()
        ship.log = random.choice(["The Lootbugs are angry!", "The Horde of lootbugs fill with rage",
                                  "The lootbugs are now standing on their legs and hissing... Yipee?"])
    
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
    "uncommon": [Monster],
    "common": [Lootbugs]
}

PROBABILITIES = {
    "rare" : 5,
    "uncommon" : 15,
    "common": 35,
    "nothing": 45
}

def get_monster() -> Monster:
    # Roll a dice
    result = roll(**PROBABILITIES)
    if result == "nothing":
        raise er.NoMonsterFlag
    
    return random.choice(GET_MONSTER[result])(rarity=result) # Gets a random monster