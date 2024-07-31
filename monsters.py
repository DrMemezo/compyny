from classes import Event, Ship, Scrap
from errors import NoMonsterFlag, RunFlag
from options import styles, wait
import random



class Monster(Event):
    """A Monster is an event which occurs and can damage the player."""
    def __init__(self, rarity:str, damage:int, is_aggresive:bool=False) -> None:
        super().__init__(rarity)
        self.damage = damage
        self.aggresive = is_aggresive
        self.hidden = False
        self.health = 3
        self.name = "Monster"

    def attack(self, ship:Ship, action:str):
        """Try to attack the player"""
        ship.log = "\n"
        if self.health > 0:
            ship.log = f"A monster attacks!"
        return ship

    def approach(self, ship:Ship):
        """Approaching the player"""
        ship.log = f"A monster approaches!"
        return ship

    def aggrevate(self):
        """Become aggressive if the player has done something"""
        self.aggresive = True

    def __str__(self) -> str:
        return f"{self.name.title()}"
    

class CommonMonster(Monster):
    def __init__(self,  damage: int, is_aggresive: bool = False) -> None:
        super().__init__(damage, is_aggresive)


class UncommonMonster(Monster):
    def __init__(self,  damage: int, is_aggresive: bool = False) -> None:
        super().__init__(damage, is_aggresive)


class RareMonster(Monster):
    def __init__(self,  damage: int, is_aggresive: bool = False) -> None:
        super().__init__(damage, is_aggresive)

def attack(**kwargs) -> Ship:
    ship = kwargs["ship"]
    monster = ship.events['monster']


    ship.log = random.choice(["You swung at the air... and missed.",
                            "Wow! Nice job hitting the air",
                            "What are you even attacking... captian?"])
    if not monster:
        return ship
        
    if monster.hidden:
        return ship
    
    if monster.health <= 0:
        ship.log = random.choice([f"You swung at the corpse of the dead {str(monster)}",
                                  f"The {str(monster)} cannot hurt you anymore, captain.",
                                  f"Dear God! It's already dead!"])
        return ship
    
    chance = random.randint(1, 100)
    if chance <= 5:
        ship.log = random.choice(["You missed!",
                                  "A swing and a miss!",
                                  "You missed. happens to the best of us."])
    elif chance <= 20:
        monster.health -= ship.damage * 1.5
        ship.log = "\t*2 -- CRITICAL HIT --"
        ship.log += f"You dealt {ship.damage * 1.5} damage to the monster. {random.choice(["Nice!", "Bravo!", "Magnificent!"])}"
    else: 
        monster.health -= ship.damage
        ship.log = f"You dealt {ship.damage} damage to the monster."
    
    ship.events['monster'] = monster
    return ship 


def alert(**kwargs):
    raise NotImplementedError

def think(**kwargs):
    ship = kwargs['ship']
    try:
        is_hidden = ship.events['monster'].hidden
    except AttributeError: # No monster
        is_hidden = True
    
    message = f"'alert': Be alerted of all the threats inside the room.\n"
    if not is_hidden:
        message += f"'attack': Chance to deal {ship.damage} damage.\n"
        message += f"'run': Turn your back to the undescribable horrors and run!"
    ship.log = message 
    return ship

def run(**kwargs):
    ship = kwargs['ship']
    monster = ship.events['monster'] 

    # Raise Run flag
    raise RunFlag

def progress(**kwargs):
    ship:Ship = kwargs['ship']
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

M_OPTIONS = {
    'attack': attack,
    'alert': alert,
    'think': think,
    'run': run,
    'progress': progress
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
    "rare": RareMonster,
    "uncommon": UncommonMonster,
    "common": CommonMonster
}

PROBABILITIES = {
    "rare" : 5,
    "uncommon" : 25,
    "common": 45,
    "nothing": 25
}

def get_monster() -> Monster:
    # Roll a dice
    chance = random.randint(1, 100) 
    # Get a monster based on that probabilaty
    previous = 0
    for rarity in ["rare", "uncommon", "common"]:
        if previous < chance <= (PROBABILITIES[rarity] + previous): # A better algorithm for chance. I will not be applying this to scraps so help me god.
            return GET_MONSTER[rarity](rarity, 10)
        previous = PROBABILITIES[rarity]
    
    raise NoMonsterFlag("No monster selected")