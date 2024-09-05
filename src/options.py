from src.classes import Event, Ship, Scrap, Weapon
import random 
from src.errors import RetreatFlag
import sys

def inspect(**kwargs) -> Ship:
    message = "There is nothing to inspect"
    events:list[Scrap] = kwargs['events']
    ship:Ship = kwargs['ship']
    event_values = []
    for event in events:
        if event.is_hidden():
            continue

        event_values.append(f"{event.name.title()}, (id: '{event.id}') has a value of {event.value}\n")
    
    if event_values:
        message = "".join(event_values)
    
    ship.log = message
    return ship

def find(**kwargs) -> Ship:
    message = ""
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    for event in events:
        try:
            if event.is_hidden():
                event.show()
                message += f"You Found a {event.name}, *{event.id}*\n"
        except:
            pass
    if not message:
        message = "Nothing of value was found..."

    ship.log = message
    return ship

def think(**kwargs) -> Ship:
    message = "You think long and hard about what to do next...\n"
    message += "'find': Find and locate any hidden items in this room\n"
    message += "'inspect': Inspect scrap that you've already found\n"
    message += "'progress': Progress to the next room\n"
    message += "'collect {id}': Add scraps to your collection\n"
    message += "'overview: Get an overview for your ship\n"
    message += "'retreat': Call it a day and get outa town\n"
    message += "'equip': Equips a Weapon that you're currently carrying\n"
    message += "\tYou can check this by using 'overview'\n"

    ship = kwargs['ship']
    ship.log = message
    return ship

def find_from_id(scrap_events:list[Scrap], id:int) -> Scrap:
    for pos, scrap in enumerate(scrap_events):
        if scrap.is_hidden(): # Cannot collect hidden scraps
            continue

        if scrap.id == id: # Matching Ids
            return scrap_events.pop(pos)
    return None 

def collect(**kwargs) -> Ship:
    events:list[Event] = kwargs['events']
    ship:Ship = kwargs['ship']
    crnt_scrap: Scrap|None = ship.current_scrap

    try:
        collect_id = int(kwargs['subject'])
    except TypeError:
        # No ID given
        ship.log = random.choice(["No scrap was specified...",
                                "You tried collecting the air. It didnt work.",
                                "What are you trying to collect, captain?"])
        return ship
    
    except ValueError:
        # Incorrect Id given
        ship.log = random.choice(["That is not a valid Id...", 
                            "No time for mistakes, captain. Look at the id.",
                            "What are you trying to collect, captain"])     
        return ship

    # Already collected
    try:
        if crnt_scrap.id == collect_id: 
            ship.log = "You have already collected this item\t...perhaps it was the wrong id?"
            return ship
    except AttributeError: # No crnt_scrap
        pass

    # Trying to find if collect is in events
    if collect_scrap := find_from_id(events, collect_id): # If id is of a valid scrap
        try:
             # Different Id
            ship.log = f"Switched out {ship.current_scrap.name}({ship.current_scrap.value}) for {collect_scrap.name}({collect_scrap.value})"            
            ship.events['scrap'].append(ship.current_scrap)
            ship.current_scrap = collect_scrap
        except AttributeError: # No scrap currently stored
            ship.log = f"Collected {collect_scrap.name.title()} for {collect_scrap.value}"
            ship.current_scrap = collect_scrap
        finally:
            return ship
    else:
        # Incorrect Id given
        ship.log = random.choice(["That is not a valid Id...", 
                            "No time for mistakes, captain. Look at the id.",
                            "What are you trying to collect, captain"])     
        return ship

def equip(**kwargs) -> Ship:
    """Equips a weapon that the ship has currently collected"""
    ship:Ship = kwargs['ship']
    
    if ship.current_scrap is None:
        ship.log = random.choice(["You equiped the air!...wait",
                                  "You haven't collected anything",
                                  "You need to collect a weapon before equipping it"])
        return ship
    
    if not type(ship.current_scrap) == Weapon:
        ship.log = random.choice(["What you have equipped isn't a weapon, captain...",
                                  "...Yeah I don't think thats gonna work out well for you.",
                                  "Only a weapon may be equipped, captain"])

        return ship
     
    if ship.current_weapon:
        ship.log = f"Switched out {ship.current_weapon.name.title()} for {ship.current_scrap.name.title()}"
        ship.current_weapon, ship.current_scrap = ship.current_scrap, ship.current_weapon # Swaps both
    else:
        ship.current_weapon = ship.current_scrap
        ship.log = f"Equipped {ship.current_scrap.name.title()}"

    return ship

def overview(**kwargs):
    """Gives an overview of the ship at the current moment of function call"""
    ship:Ship = kwargs['ship']
    crt_scrap:Scrap|None = ship.current_scrap
    crt_weapon:Weapon|None = ship.current_weapon
    

    message = "SHIP STATUS---\n"
    message += f"SHIP HEALTH: {ship.health}\n"
    message += f"SHIP POINTS: {ship.points}\n"
    # WEAPON    
    message += "CURRENT WEAPON: "
    if crt_weapon is None:
        message += "UNEQUIPED"
    else:
        message += f"{crt_weapon.name} -- {crt_weapon.description}\n"
        message += f"\tDAMAGE: {crt_weapon.damage}\n"   
    # SCRAP
    message += f"CURRENT SCRAP: "

    if crt_scrap is None:
        message += "UNSELECTED\n"
    else:
        message += f"{crt_scrap.name} -- {crt_scrap.description}\n"
        message += f"\tPOINTS: {crt_scrap.value}\n"
        message += f"\tRARITY: {crt_scrap.rarity.title()}\n"

    message += f"INSANITY: {ship.insanity}\n"
    
    ship.log = message
    return ship
        
def retreat(**kwargs):
    raise RetreatFlag

def exit(**kwargs):
    sys.exit(0)

# Options for the player
OPTIONS = {
    'exit': exit,
    'inspect' : inspect,
    'find' : find,
    'think' : think,
    'collect': collect,
    'overview': overview,
    'retreat': retreat,
    'equip': equip
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
    "overview": "turquoise2",
    "equip": "light_yellow3"
}

# Stores the interval for slow printing for each action
wait = {
    "think": 0.001,
    "advise": 0.02,
    "find": 0.03,
    "inspect": 0.03,
    "overview": 0.025,
    "collect": 0.03,
    "progress": 0.05,
    "equip": 0.05
}