# LETHAL (PROTO) COM-PY-NY
from time import sleep
import csv
import random
from rich.console import Console
import classes

# Console class from rich, to make text prettier to look at.
CONSOLE = Console()
styles = {
    "default" : "bold white on blue",
    "danger" : "bold white on dark red",
    "info": "bold white on green"
}


def main():
    # Intro to the moon, a spooky description, etc. 
    # DISABLED: print_intro()
    # Play state
    play()
    # End state
    end()

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

def play():
    global CONSOLE
    alive:bool = True 
    while alive:
        events:list = get_events()
        for event in events:
            # Print event info
            slow_print(event.__str__(), wait=0.05)

        # Prompt user for input
        slow_print("What to do now?", style=styles['info'], wait=0.02)
        action = input()

        # Print out user action
        CONSOLE.print(f"You did this {action}")
        
        # See if user lives or dies
        alive = random.choice([True, False])

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

def end(dead:bool=True):
    style:str = "green" 
    if dead:
        style = "bold white on red"
    
    slow_print("GAME OVER", style=style)

if __name__ == "__main__":
    main()