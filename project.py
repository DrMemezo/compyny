# LETHAL (PROTO) COM-PY-NY
# Console class from rich, to make text prettier to look at.
from dependencies import *

CONSOLE = Console()
PATHS = {
    'moons': 'assets/moons.csv'
}

def main():
    # Game's title card
    # UNDEVELOPED: titlecard()
    
    # Initialising the ship:
    # DISABLED: ship_init()
    main_ship:Ship = Ship()
    # Intro to the moon, a spooky description, etc. 
    #DISABLED: print_intro()
    # Play state
    main_ship = play(main_ship)
    # End state
    end(main_ship)

def ship_init() -> Ship:
    
    
    slow_print("WHAT IS YOUR NAME,", wait=0.2, style=styles['default'])
    slow_print("T R A V E L L E R ?", wait=0.2, style=styles['danger'])
    name = input().strip()
    ship = Ship(name=name)
    ship = get_events(ship)
    
    return ship
    

def print_intro():
    intro:dict = get_intro()
    slow_print(f"{intro['moon'].upper()}",style=styles["default"], wait=0.2)
    slow_print(f"\n\t{intro['description']}", wait=0.02)
    # TODO: Add a prompt to show entry into the bunker


def get_intro() -> dict:
    """Gets a dictionary defined as {'moon': <moon>, 'description':<desc>}
    from moons.csv"""
    path = Path(PATHS["moons"]) # Path for Path in the path for path
    
    if not path.exists():
        raise FileNotFoundError
    
    with open(path) as file:
        moons:list = list(csv.DictReader(file,delimiter='|', skipinitialspace=True))
    
    return random.choice(moons)


def slow_print(message:str, wait:float=0.1,
                style:str="white", end:str="\n"):
    """NOTE: Only pass strings!!"""
    
    if message == "": # Does not print whitespaces
        return
    
    global CONSOLE

    for char in message:
        CONSOLE.print(char,style=style, end="")
        sleep(wait)
    print(end=end)    


def play(ship:Ship):
    global CONSOLE
    alive:bool = True 
    while alive:
        # TODO: Remove the below line after adding ship_init()
        ship = get_events(ship)
        
        try:
            for event in ship.events['scrap']:
                if not event.is_hidden(): # Print event info
                    slow_print(event.__str__(), wait=wait['overview'])
        except KeyError: # No scraps in the current room
                pass
        
        try: # Monster approach
            ship.log = ship.events['monster'].approach()
            slow_print(ship.log, wait=0.05, style="deep_pink4")
        except AttributeError: # No monster 
            pass
        # Prompt user for input
        slow_print("What to do now?", style=styles['overview'], wait=wait['advise'])


        while True:             
            think_count = 0
            
            # Get action 
            action, subject = get_action()
            
            # SCRAP OPTIONS

            try:
                ship = OPTIONS[action](ship=ship, events=ship.events['scrap'], subject=subject) # gt action on all scraps
                slow_print(ship.log, wait=wait[action], style=styles[action]) # Print out result (If any)
            except KeyError:
                think_count += 1
            except RetreatFlag:
                ship.exit_flag = RetreatFlag
                return ship
            
            # Reset log so that it dosen't repeat
            ship.log = ""               
            
            # MONSTER OPTIONS

            try:
                ship = M_OPTIONS[action](ship=ship) # Result of action on the monster
                slow_print(ship.log, wait=wait[action], style=styles[action]) # Print out result
            except KeyError:
                think_count += 1
            except RunFlag:
                show_run(ship=ship)
                break
            except ProgressFailFlag:
                ship.exit_flag = ProgressFailFlag
                return ship
            
            ship.log = ""
            
            # Monster attacks
            try:
                ship = ship.events['monster'].attack(ship, is_progressing=False)
                slow_print(ship.log, wait=0.05, style="orange_red1")
            except AttributeError: # No Monster selected
                pass
            except KilledFlag:
                ship.exit_flag = KilledFlag
                return ship
            except CustomKilledFlag:
                ship.exit_flag = CustomKilledFlag
                return ship
            except KeyError:
                think_count += 1

            # Think Message
            if think_count == 2:
                print_think()


            # When player progresses
            if action == "progress":
                break
    
    return ship

def show_run(ship) -> None:
    slow_print("You ran!", wait=0.1, style="bold orange3")
    try:
        message = f"While running, you left {ship.current_scrap.name.title()}, worth {ship.current_scrap.value} points"
    except AttributeError:
        return 
    slow_print(message, style="red on light_cyan1", wait=0.05)

def get_events(ship):
    ship.get_scraps() # Get scrap events
    try:
        ship.events["monster"] = get_monster()
    except NoMonsterFlag:
        ship.events["monster"] = None
    return ship

def show_retreat(ship:Ship):
    
    message = random.choice(["Another day, Another salvage.",
                             "Same time tomorrow. 9' o clock.",
                             "You run and run, but the horrors will always be there with you."])
    slow_print(message, style="red3 bold")
    try:
        message = f"While retreating, you left {ship.current_scrap.name.title()}, worth {ship.current_scrap.value} points"
    except AttributeError:
        return
    
    slow_print(message, style="red on light_cyan1", wait=0.05)


def print_think():
    random.seed()
    message = random.choice(["Think, captian. Think!",
                                "Might be helpful to THINK that over",
                                "Think carefully about what you need to do..."])

    pattern = r"think(?:[?!.])?"

    advice = re.split(pattern, message, flags=re.IGNORECASE)
    advice = iter(advice)
    find_res = re.findall(pattern, message, flags=re.IGNORECASE)
    find_res = iter(find_res) # To convert list into an iterator


    while True:
        try:
            slow_print(next(advice), style=styles['advise'], wait=wait['advise'], end='')
            slow_print(next(find_res), style=styles['advise_bold'], wait=wait['advise'], end='')
        except StopIteration:
            break
    print()

def get_action() -> str:
    """Returns an action(i.e collect, find) and the object to perform it on"""
    while True:    
        action = re.sub(r" +", " ", input().strip().lower()) # Removing any double spaces to one 
        try:
            return validate_action(action)
        except ValueError:
            print_think()
            continue

def validate_action(action):
    subject:None|str = None

    if match := re.findall(r" ", action):
        if len(match) >= 3:
            raise ValueError("More than three args given")

    if match := re.match(r"^(\w+) (\w+)$", action):
        action = match.group(1)
        subject = match.group(2)
    
    return action, subject

def end(ship:Ship):
    """End State for the game"""

    if ship.exit_flag == RetreatFlag:
        show_retreat(ship)
    else:
        monster:Monster = ship.events['monster']
        message = monster.get_message(ship.exit_flag)
        slow_print(message=message) #TODO: make this aesthetic

    style:str = "green" 
    if ship.is_dead():
        style = "bold white on red"
    
    slow_print("GAME OVER", style=styles['default'])
    slow_print(f"Points: {ship.points}", style=styles['default'])

if __name__ == "__main__":
    main()