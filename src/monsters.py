try:
    from classes import Event, Ship, Weapon
    import errors as er
    from options import styles, wait
    from roll import roll
except ModuleNotFoundError:
    from src.classes import Event, Ship, Weapon
    import src.errors as er
    from src.options import styles, wait
    from src.roll import roll

import random


class Monster(Event):
    """A Monster is an event which occurs and can damage the player."""
    def __init__(self, rarity:str="common",name="Monster",description="The Monster Template",
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
    
    def attack_response(self) -> str:

        msg += self.aggrevate()
        msg += "\n"
        return msg

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

    def progress_response(self, ship:Ship) -> Ship:
        ship = self.attack(ship, crit=100, hit=0, miss=0, is_progressing=True)
        ship.events['monster'] = self if self.persistant else None
        return ship

    def __str__(self) -> str:
        return f"{self.name.title()}"
    
class Lootbugs(Monster):
    def __init__(self, rarity:str="common", name="Lootbugs", description="A horde of happy horders",
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

    def __init__(self, rarity:str="uncommon", name="Bracken", description="A leavy maroon marauder", damage: int = 7, health: int = 6,
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
    def __init__(self, rarity:str="rare", name="Jester", description="An ominous box with legs", damage: int = 100, health: int = 1000,
                  is_aggresive=False, is_hidden=False, is_persistant=True) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.rooms = 0 # How many rooms the ship has travelled since it was winding
        self.wind = random.randint(6, 9) # Counts down until the jester is aggresive
        self.have_we_met = False
    
    def approach(self, msgs: list[str] = ["A box with legs appears behind you...",
                                          "An ominious box with legs approaches!",
                                          "It's a... box with legs?"]) -> str:

        if self.aggresive:
            return random.choice(["THE BANGS OF IT'S FOOTSTEPS FOLLOW YOU CEASELESSLY",
                                  "TICK. TOCK.",
                                  "STAND STILL. ACCEPT WHAT'S GETTING TO YOU."])
        if self.wind <= 0:
            return self.aggrevate()
        
        if self.have_we_met:
            return random.choice(["The Chimes ring throughout the hall",
                                  "That's the way the money goes.",
                                  "The chimes become louder, somehow..."])        
        
        self.have_we_met = True
        return super().approach(msgs)

    def attack_response(self) -> str:
        """If player is in the same room as the Jester, allow them to attack"""
        if self.rooms != 0:
            raise er.CannotReachFlag
        
        self.wind -= 1
        return random.choice(["You got a bad feeling from doing that...",
                              "I don't think that was the right call",
                              "That didn't do anything..."])
       
    def run_response(self) -> str:
        self.rooms += 1
        self.wind -= 1
        if self.aggresive:
            return random.choice(["YES. IT'S ALL YOU CAN DO.",
                                  "KEEP RUNNING.",
                                  "FOOLISH TO THINK YOU CAN OUTRUN ME."])
        
        return random.choice(["The chimes echo throughtout the halls",
                              "Merrily Merrily Merilly Merilly",
                              "You look behind you and see it opening it's lid..."])

    def progress_response(self, ship: Ship) -> Ship:
        self.rooms += 1  
        self.wind -=1     
        return ship

    def set_message(self, kill: str = "It found you. Tore at you. It didn't leave a trace.",
                    progfail: str = "Progress failed",
                    custom: str = "Custom Killed message") -> None:
        return super().set_message(kill, progfail, custom)

    def aggrevate(self, msgs: list[str] = ["THE JESTER IS COMING",
                                           "POP GOES THE WEASEL",
                                           "RUN WHILE YOU CAN. IT'S COMING"]) -> str:
        return super().aggrevate(msgs)

    def attack(self, ship: Ship,
                crit: int = 0, hit: int = 100, miss: int = 0, **kwargs) -> Ship:
        """Instead of basic combat, the jester will wind, find the player and kill them"""
        # Winding
        if not self.aggresive:
            self.wind -= 1
        
            if self.wind == 0:
                ship.log = self.aggrevate()
            else:
                ship.log = random.choice(["It's winding down...",
                                            "Round the town and back again",
                                            "It's chimes are getting quicker... and quiter"])  
            return ship
    
        # Chase
        self.rooms -= 1
        
        if self.rooms == 0: # Kill
            raise er.KilledFlag
        else:
            ship.log = random.choice(["IT'S GETTING CLOSER",
                                      "KEEP RUNNING",
                                      "IT WILL FIND YOU. KEEP GOING"])
        return ship

# -- MONSTER RELATED FUNCTIONS --
def attack(**kwargs) -> Ship:
    ship:Ship = kwargs["ship"]
    monster:Monster = ship.events['monster']
    weapon:Weapon = ship.current_weapon

    if not weapon:
        ship.log += "You don't have a weapon!"
        return ship

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

    try:
        ship.log = monster.attack_response()
    except er.CannotReachFlag:
        ship.log = "You're in another room, You cannot attack"
        return ship 

    # TODO: Instead of hardcoding these values, use values from the weapon the ship has
    result = roll(**weapon.stats)
    match result:
        case "miss":   
            ship.log += random.choice(["You missed!",
                                        "A swing and a miss!",
                                        "You missed. happens to the best of us."])
        case "crit":
            monster.health -= (weapon.damage * 1.5) // 1
            ship.log = "\t -- CRITICAL HIT --"
            ship.log += f"\nYou dealt {(weapon.damage * 1.5) // 1} damage to the {str(monster)}. {random.choice(["Nice!", "Bravo!", "Magnificent!"])}"
        case "hit":
            monster.health -= weapon.damage
            ship.log += f"\nYou dealt {weapon.damage} damage to the {str(monster)}."
    
    if monster.is_dead():
        ship.log += f"\nThe {str(monster)} has been slained..."
    
    weapon.uses -= 1
    if weapon.uses <= 0:
        ship.log += f"\nThe {weapon.name.title()} broke!"
        weapon = None
    
    ship.current_weapon = weapon   
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
        ship = monster.progress_response(ship)
    except AttributeError: # No monster 
        pass
    
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
    "rare": [Jester],
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
    """Gets a monster"""
    result = roll(**PROBABILITIES)
    
    #TODO: Make rare and uncommon progressively more apparent.

    if result == "nothing":
        raise er.NoMonsterFlag
    
    
    return random.choice(GET_MONSTER[result])() # Gets a random monster