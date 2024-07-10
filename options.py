from classes import Event, Ship, Scrap
import random 
from errors import RetreatFlag


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