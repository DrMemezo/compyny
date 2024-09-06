try:
    from classes import Event, Ship, Weapon
    import errors as er
    from options import styles, wait
    from roll import Chance, roll
    from utils import SFX
except ModuleNotFoundError:
    from src.classes import Event, Ship, Weapon
    import src.errors as er
    from src.options import styles, wait
    from src.roll import Chance, roll
    from src.utils import SFX

import random
from playsound import PlaysoundException
from playsound import playsound as ps

def playsound(file) ->None:
    try:
        ps(file)
    except TypeError:
        file = str(file)
        ps(file)

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

    def stare_response(self) -> str:
        return random.choice([f"You looked at the {str(self)}.The {str(self)} looked at you...",
                              f"You held a staring competition with the {str(self)}",
                              f"Ah yes. Stare at it. That'll show 'em."])    
    
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
                playsound(SFX["hurt"]) 
                ship.log += f"\t-- CRITICAL DAMAGE SUSTAINED --\n\tThe {self.name} dealt {damage} damage"
            case "hit":
                damage = self.damage
                ship.health -= damage
                playsound(SFX["hurt"])
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
        msg = self.aggrevate()
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

    def attack_response(self) -> str:
        self.stare_counter += 1
        return super().attack_response()
    
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

    def stare_response(self) -> str:

        """Stare at the bracken, same thing as alert_response, except it doesn't show the bracken""" 
        if self.is_hidden():
            raise AttributeError
        
        if self.aggresive:
            return random.choice(["You looked deeply into those blood red eyes.",
                                  "Shouldn't you be attacking it?",
                                  "... You looked into it's eyes and felt a deep bloodthirst"]) #Braken is already aggresive
 
        self.stare_counter += 1

        if self.stare_counter == 4:
            message = self.aggrevate()
        else:
            message = random.choice(["You hear the Bracken snarling...",
                                     "You and the Bracken feel the tension rising...",
                                     "The Bracken creeps closer"])
        
        return message

    def alert_response(self) -> str:
        """If the player uses alert, it shows them that a bracken is here and 
        prolongs their demise, however, if the bracken is stared at too long, it becomes aggresive..."""
        
        if self.hidden:
            message = "You found a bracken sulking in the shadows..."
            self.stare_counter += 1
            self.hidden = False
            return message

        return self.stare_response()

class Jester(Monster):
    def __init__(self, rarity:str="rare", name="Jester", description="An ominous box with legs", damage: int = 100, health: int = 1000,
                  is_aggresive=False, is_hidden=False, is_persistant=True) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.rooms = 0 # How many rooms the ship has travelled since it was winding
        self.INITAL_WIND = random.randint(6, 9)
        self.wind = self.INITAL_WIND # Counts down until the jester is aggresive
        self.have_we_met = False
    
    def approach(self, msgs: list[str] = ["A box with legs appears behind you...",
                                          "An ominious box with legs approaches!",
                                          "It's a... box with legs?"]) -> str:
        if not self.have_we_met:
            self.have_we_met = True
            return super().approach(msgs)


        if self.aggresive:
            self.room -=1
            return random.choice(["THE BANGS OF IT'S FOOTSTEPS FOLLOW YOU CEASELESSLY",
                                  "TICK. TOCK.",
                                  "STAND STILL. ACCEPT WHAT'S GETTING TO YOU."])
        return self.wind_down()

    def wind_down(self) -> str:
        if self.aggresive:
            return ""

        self.wind -= 1
        
        if self.wind <= 0:
            playsound(SFX["Jester"]["almost"])
            # I had intended to make the "pop" asynchronus with the message, but i couldn't figure it out
            playsound(SFX["Jester"]["pop"])
            return self.aggrevate()
        if self.wind < 3:
            playsound(SFX["Jester"]["extreme"])
            return random.choice(["You have to run.",
                                  "Get out of here before it's too late.",
                                  "It'll be here soon."])
        
        if  3 < self.wind < self.INITAL_WIND - 1:
            playsound(SFX["Jester"]["mild"])
            return random.choice(["The chimes echo throughtout the halls",
                                "tick tock",
                                "That's the way the money goes"])
        
        if self.wind == (self.INITAL_WIND - 1):
            playsound(SFX["Jester"]["start"])
            return random.choice(["Something bad's about to happen...",
                                  "You might need to run...",
                                  "That doesn't sound good..."])
 
    def attack_response(self) -> str:
        """If player is in the same room as the Jester, allow them to attack"""

        if self.rooms != 0:
            raise er.CannotReachFlag
        

        return random.choice(["You got a bad feeling from doing that...",
                              "I don't think that was the right call",
                              "That didn't do anything..."])
       
    def run_response(self) -> str:
        self.rooms += 1
        if self.aggresive:
            return random.choice(["YES. IT'S ALL YOU CAN DO.",
                                  "KEEP RUNNING.",
                                  "YOU CAN'T KEEP RUNNING : ) ."])
        return self.wind_down()
        

    def progress_response(self, ship: Ship) -> Ship:
        self.rooms += 1  
        ship.log = self.wind_down()     
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
            ship.log = self.wind_down()
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

class Hallucinations(Monster):
    def __init__(self, rarity: str = "common", name="Hallucination", description="spooky", damage: int = 7, health: int = 10, is_aggresive=False, is_hidden=False, is_persistant=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
    
    
    def hallucinate(self, ship:Ship) -> Ship:
        ship.log = random.choice(["There was something there! You know there was!",
                                  "Hmmph. There was nothing there",
                                    "Must've been the wind."])
        ship.insanity += 10
        ship.events['monster'] = None
        return ship
     
    def approach(self, msgs: list[str] = ["Is that the voice of a little girl?",
                                          "Something bad is coming your way!",
                                          "You gotta run, captain!",
                                          "The pitter patter of death approaches!"]) -> str:
        return super().approach(msgs)

    # The following methods just raise the hallucinating flag
    def stare_response(self) -> str:
        raise er.HallucinatingFlag
    def attack_response(self) -> str:
        raise er.HallucinatingFlag
    def alert_response(self):
        raise er.HallucinatingFlag
    # --   
    def progress_response(self, ship: Ship) -> Ship:
        ship.events['monster'] = None
        return ship



    def attack(self, ship: Ship, **kwargs) -> Ship:
        ship.log = random.choice(["You feel as if something is following you",
                                  "Is that a bracken in the corner?",
                                  "You feel as if something is watching you...",
                                  ""])
        ship.insanity += 3
        return ship

class GhostGirl(Hallucinations, Monster):
    def __init__(self, rarity: str = "common", name="Ghost Girl", description=":]", damage: int = 0, health: int = 1, is_aggresive=False, is_hidden=True, is_persistant=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.INITIAL_PATIENCE = 9
        self.patience = self.INITIAL_PATIENCE

    def approach(self) -> str:
        return ""

    def progress_response(self, ship: Ship) -> Ship:
        """Disappears if the player hasn't been alerted of the little girl"""
        if not self.persistant:
            ship.events['monster'] = None
            ship.insanity += 30
        
        self.hidden = True

        return ship

    def run_response(self) -> str:
        if not self.persistant:
            return ""
        self.hidden = True

        return random.choice(["The laugh of the little girl rings throughout the halls",
                 "The dainty steps of the little girl keep approaching",
                 "The laughing doesn't stop..."])

    def hallucinate(self, ship: Ship) -> Ship:
        # Case 1: The player is encountering the ghost girl
        if not self.persistant:
            self.hidden = False
            self.persistant = True
            ship.log = "You saw a little girl, before she disappeared. She was grinning widely."
            ship.insanity += 50
            return ship

        # Case 2: The player has moved to a new room and is encountering the ghost girl
        if self.is_hidden():
            playsound(SFX["ghost"])
            self.hidden = False
            ship.log = random.choice(["The ghost girl is there. smiling",
                                      ":)",
                                      "The ghost girl is smiling"])
            return ship
        # Case 3: The player has already encountered the ghost girl in the room       
        ship.insanity += 50
        ship.log = random.choice(["Im already gone :)",
                                  "w her e is s h?e",
                                  "You fee ls  o di so rie nte  .d"])
        return ship

    def attack(self, ship: Ship, **kwargs) -> Ship:
        if not self.persistant:
            return ship
        
        self.patience -= 1
        if self.patience <= 0:
            raise er.KilledFlag
        
        def new_message():
            msgs = ["Isn't this getting boring captain?",
                    "Like it's the same thing over and over and o v e r a n d  o  v  e  r",
                    "Don't you want more?",
                    "Don't you want it to end?",
                    "How long are you gonna keep doing this?",
                    "Just leave. You know you want to.",
                    "Really? You're still going?",
                    "fine. i'll let you end :>"] 
            i = self.INITIAL_PATIENCE - (self.patience + 1) 
            return msgs[i]

        ship.log = new_message()
        
        return ship

    def set_message(self, kill: str = "You are dead. You bashed your skull into the wall, or killed yourself...or maybe just gave up :>", progfail: str = "Progress failed", custom: str = "Custom Killed message") -> None:
        return super().set_message(kill, progfail, custom)   

class Butler(Monster):
    def __init__(self, rarity: str = "common", name="Butler", description="If a blobfish could look dapper...", damage: int = 5, health: int = 5, is_aggresive=False, is_hidden=False, is_persistant=False) -> None:
        super().__init__(rarity, name, description, damage, health, is_aggresive, is_hidden, is_persistant)
        self.patience = 4 # Gets aggresive when loses patience
    
    def approach(self, msgs: list[str] = ["A rather disturbing man approaches!",
                                          "You see a Butler sweeping away!",
                                          "A mysterious butler sweeps away!"]) -> str:
        return super().approach(msgs)

    def attack_response(self) -> str:
        return super().attack_response()

    def aggrevate(self, msgs: list[str] = ["The Butler has pulled out a knife!",
                                           "The Butler has had enough of your s^!t!",
                                           "The Butler is gonna make you a mystery soon!"]) -> str:
        return super().aggrevate(msgs)
        self.patience = 0

    def attack(self, ship: Ship, crit: int = 0, hit: int = 100, miss: int = 0, **kwargs) -> Ship:
        if self.aggresive:
            return super().attack(ship, crit, hit, miss, **kwargs)
        self.patience -= 1
        # Butler losing his patience
        match self.patience:
            case 3:
                ship.log = "The Butler stops sweeping..."
            case 2:
                ship.log = "The Butler stares at you repulsively..." 
            case 1:
                ship.log = "The Butler has put his broom away... uh oh."
            case 0:
                ship.log = self.aggrevate()
        return ship
        
    def slain_response(self, ship:Ship) -> Ship:
        ship.log = "The Butler has fallen... and he can't get up!"
        ship.log += "\n The Butler dropped an item!"
        ship.events['scrap'].append(
            Weapon("weapon", {"crit":20, "hit":20, "miss":60}, 50, 
                   name="Kitchen Knife", description="A Pristine Knife, prime murder weapon",
                   value=30, damage=6)
        )
        return ship

    def set_message(self, kill: str = "In it's blind rage, the Butler struck your heart!",
                    progfail: str = "As you were progressing, you felt a sharp pain in your spine", 
                    custom: str = "Custom Killed message") -> None:
        return super().set_message(kill, progfail, custom)

class Portal(Monster):
    pass
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
        ship.insanity += 5
        return ship
        
    if monster.hidden and not isinstance(monster, Hallucinations):
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
    except er.HallucinatingFlag:
        ship = monster.hallucinate(ship)
        return ship

    # TODO: Instead of hardcoding these values, use values from the weapon the ship has
    result = weapon.chance.roll()
    match result:
        case "miss":   
            ship.log += random.choice(["You missed!",
                                        "A swing and a miss!",
                                        "You missed. happens to the best of us."])
        case "crit":
            monster.health -= (weapon.damage * 1.5) // 1
            playsound(SFX["attack"])
            ship.log += "\t -- CRITICAL HIT --"
            ship.log += f"\nYou dealt {(weapon.damage * 1.5) // 1} damage to the {str(monster)}. {random.choice(["Nice!", "Bravo!", "Magnificent!"])}"
        case "hit":
            monster.health -= weapon.damage
            playsound(SFX["attack"])
            ship.log += f"\nYou dealt {weapon.damage} damage to the {str(monster)}."
    
    if monster.is_dead():
        try:
            ship = monster.slain_response(ship)
        except AttributeError:
            ship.log += f"\nThe {str(monster)} has been slained..."
            
    
    weapon.uses -= 1
    if weapon.uses <= 0:
        ship.log += f"\nThe {weapon.name.title()} broke!"
        weapon = None
    
    ship.current_weapon = weapon   
    ship.events['monster'] = monster
    return ship 
 
def alert(**kwargs) -> Ship:
    ship:Ship = kwargs['ship']
    monster:Monster = ship.events['monster']
    ship.log = ""
    ship.insanity += 5
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
    except er.HallucinatingFlag:
        ship = monster.hallucinate(ship)
        return ship
        
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
    ship:Ship = kwargs['ship']
    try:
        is_hidden = ship.events['monster'].is_hidden()
    except AttributeError: # No monster
        is_hidden = True
    
    message = f"'alert': Be alerted of all the threats inside the room.\n"
    if not is_hidden:
        message += f"'attack': Chance to deal {ship.current_weapon.damage} damage.\n"
        message += f"'run': Drop everything and run!\n"
        message += "'stare': Stare at the monster... if that will do anything..."
    ship.log = message 
    return ship

def run(**kwargs):
    # Raise Run flag
    raise er.RunFlag

def stare(**kwargs) -> Ship:
    ship:Ship = kwargs['ship']
    monster:Monster|Hallucinations = ship.events['monster']
    try:
        ship.log = monster.stare_response()
    except AttributeError:
        ship.log = random.choice(["You stared into an eternal darkness",
                                  'What a "nice" "view" of this "wonderful" place',
                                  "You wanna hold staring competitions with ghosts? I wouldn't stop you..."])
    except er.HallucinatingFlag:
        ship = monster.hallucinate(ship)
    return ship 

def progress(**kwargs) -> Ship:
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

def collect(**kwargs) -> Ship:
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
    'collect': collect,
    'stare': stare
}

styles.update({
    'attack' : "medium_violet_red",
    'run': "bold bright_red",
    'alert': "dark_orange3",
    'stare': "light_goldenrod3"
})

wait.update({
    'attack': 0.09,
    'run': 0.1,
    'alert': 0.05,
    'stare': 0.05
})

GET_MONSTER = {
    "rare": [Jester, GhostGirl],
    "uncommon": [Bracken],
    "common": [Lootbugs, Butler],
    "hallucination": [Hallucinations]
}


def get_monster(chance:Chance) -> Monster:
    """Gets a monster"""
    result = chance.roll()
    
    if result == "nothing":
        raise er.NoMonsterFlag
    
    return random.choice(GET_MONSTER[result])() # Gets a random monster