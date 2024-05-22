# LETHAL (PROTO) COM-PY-NY
from time import sleep
import csv
import random
from rich.console import Console
import classes 
from classes import styles, wait, Ship
# Console class from rich, to make text prettier to look at.
CONSOLE = Console()

def main():
    # Game's title card
    # UNDEVELOPED: titlecard()
    
    # Initialising the ship:
    # DISABLED: main_ship:Ship = ship_init()
    # Intro to the moon, a spooky description, etc. 
    # DISABLED: print_intro()
    # Play state
    play(main_ship)
    # End state
    end(main_ship)

def ship_init() -> Ship:
    
    
    slow_print("WHAT IS YOUR NAME,", wait=0.2, style=styles['default'])
    slow_print("T R A V E L L E R ?", wait=0.2, style=styles['danger'])
    name = input().strip()
    return Ship(name=name)
    

def print_intro():
    intro:dict = get_intro()
    slow_print(f"{intro['moon'].upper()}",style=styles["default"], wait=0.2)
    slow_print(f"\n\t{intro['description']}", wait=0.02)


def get_intro() -> dict:
    """Gets a dictionary defined as {'moon': <moon>, 'description':<desc>}
    from moons.csv"""
    with open("moons.csv") as file:
        moons:list = list(csv.DictReader(file,delimiter='|', skipinitialspace=True))
    
    return random.choice(moons)


def slow_print(message:str, wait:float=0.1,
                style:str="white", end:str="\n"):
    """NOTE: Only pass strings!!"""
    global CONSOLE

    for char in message:
        CONSOLE.print(char,style=style, end="")
        sleep(wait)
    print(end=end)    


def play(ship:Ship):
    global CONSOLE
    alive:bool = True 
    while alive:
        # Show progression into the next area
        next_room()
        events:list = get_events() # Gets a list of events
        for event in events:
            # Print event info
            if not event.is_hidden():
                slow_print(event.__str__(), wait=wait['overview'])

        # Prompt user for input
        slow_print("What to do now?", style=styles['info'], wait=wait['advise'])
        action = input().strip().lower()
                
        while action != "progress":
            try:
                slow_print(classes.OPTIONS[action](events), wait=wait[action], style=styles[action])
            except KeyError:
                CONSOLE.print("psst... it maybe helpful to.. THINK.. about your actions...",
                              style=styles['advise'])
            finally:
                action = input().strip()

        # See if user lives or dies
        alive = random.choice([True, False])

def next_room():
    global CONSOLE
    message = random.choice(["Walking through the maze of endless hallways, you find the next room.",
                             "You feel a cold chill up your spine as you walk into the next room",
                             "You hear sounds and scrapes in the distance as you walk into the next room",
                             "Your flashlight flickers in the ominous darkness, yet you find your way to the next room."])
    
    slow_print(message,wait=0.05, style="bold bright_cyan")

def get_events() -> list:
    """Returns a list of event objects"""
    events = []
    limit = random.randint(1, 3)
    for _ in range(0, limit):
        # Basic percentage
        chance = random.randint(1, 100)
        if chance < 15: # "rare" has a 15% chance
            rarity = "rare"
        elif chance < 45: # "uncommon" has a 45% chance
            rarity = "uncommon"
        elif chance < 85: # "common" has a 85% chance
            rarity = "common"
        else:
            continue
        events.append(classes.Scrap(rarity=rarity))
    
    return events

def end(ship:Ship, dead:bool=True):
    style:str = "green" 
    if dead:
        style = "bold white on red"
    
    slow_print("GAME OVER", style=styles['default'])
    slow_print(f"Points: {ship.scraps}", style=styles['default'])

if __name__ == "__main__":
    main()