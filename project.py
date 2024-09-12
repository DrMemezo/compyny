# LETHAL (PROTO) COM-PY-NY
# Console class from rich, to make text prettier to look at.
from dependencies import *


def main():
    # Game's title card
    # UNDEVELOPED: titlecard()
    
    # Initialising the ship:
    main_ship:Ship = ship_init()
    # Intro to the moon, a spooky description, etc. 
    print_intro()
    # Play state
    main_ship = play(main_ship)
    # End state
    end(main_ship)

def validate_paths(path_dir:dict[str,Path|dict]) -> bool:
    """Recursive function to check if the paths exist."""
    for path in path_dir.values():
        if type(path) == dict:
            validate_paths(path)
            continue
        
        if not path.exists(): # Base Case
            raise FileNotFoundError(f"Path does not exits: {path}")
        
        if path.is_file():
            continue

def ship_init() -> Ship:
    validate_paths(PATHS)
    validate_paths(SFX)
    ship = Ship()
    ship = get_events(ship)
    
    return ship

def print_intro():
    intro:dict = get_intro()
    slow_print(f"{intro['moon'].upper()}",style=styles["default"], wait=0.2)
    slow_print(f"\n\t{intro['description']}", wait=0.02)
    # TODO: Add a prompt to show entry into the bunker

def get_intro(path=PATHS["moons"]) -> dict:
    """Gets a dictionary defined as {'moon': <moon>, 'description':<desc>}
    from moons.csv"""
    
    if not path.exists():
        raise FileNotFoundError
    
    with open(path) as file:
        moons:list = list(csv.DictReader(file,delimiter='|', skipinitialspace=True))
    
    return random.choice(moons)

def play(ship:Ship):
    global CONSOLE
    alive:bool = True 
    while alive:
        ship = get_events(ship=ship)
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
                ship = show_run(ship=ship)
                ship.insanity += 10
                break
            except (ProgressFailFlag, KilledFlag, CustomKilledFlag) as e:
                ship.exit_flag = type(e)
                return ship
            
            ship.log = ""
            
            # Monster attacks
            try:
                ship = ship.events['monster'].attack(ship, is_progressing=False)
                slow_print(ship.log, wait=0.05, style="orange_red1")
            except AttributeError: # No Monster selected
                pass
            except (KilledFlag, CustomKilledFlag) as e:
                ship.exit_flag = type(e)
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

def show_run(ship:Ship) -> None:
    slow_print("You ran!", wait=0.1, style="bold orange3")
    try:
        message = f"While running, you left {ship.current_scrap.name.title()}, worth {ship.current_scrap.value} points"
    except AttributeError:
        pass 
    else:
        ship.current_scrap = None
        slow_print(message, style="red on light_cyan1", wait=0.05)
    
    try:
        ship.log = ship.events['monster'].run_response()
    except AttributeError: # Monster is not persistant
        ship.events['monster'] = None 
    else:
        slow_print(ship.log, wait=wait['attack'], style=styles['attack'])
    return ship

def get_events(ship:Ship):
    ship.get_scraps() # Get scrap events
    monster:Monster|None = ship.events["monster"]
    # Monster persistancy
    try:
        if monster.persistant:
            return ship
    except AttributeError:
        pass
    
    try:
        ship.events["monster"] = get_monster(ship.monster_chance)
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

def parse_for_slowprint(msg:str, key:str) -> list:
    """Returns an list with which slowprint can work with"""
    pattern = rf"\b{re.escape(key)}\b"
    matches = re.finditer(pattern, msg, flags=re.IGNORECASE)
    last_end = 0
    parsed = []
    for match in matches:
        start, end = match.span()
        if last_end < start: # not the keyword
            parsed.append(msg[last_end:start])

        # Add the keyword
        parsed.append(match.group(0))
        # update last_end
        last_end = end

    # If words remaining
    if last_end < len(msg):
        parsed.append(msg[last_end:])

    # If first word is keyword
    if re.match(pattern, parsed[0], flags=re.IGNORECASE):
        parsed.insert(0, "")

    return parsed
        
def slow_print_sequence(parsed:list[str],
                        normal=("grey50", 0.02),
                        special=("bold underline grey50", 0.025)):

    try:
        norm_style, norm_wait = normal
        spec_style, spec_wait = special
    except ValueError:
        raise("Invalid parameters passed. Format:(style, wait)")


    
    for i, msg in enumerate(parsed):
        if i % 2 == 0:
            slow_print(msg, style=norm_style, wait=norm_wait, end="")
            continue
        slow_print(msg, style=spec_style, wait=spec_wait, end="")
    print()
    """Takes in a parsed list as input, and slow_prints it with special styles and intervals"""
def print_think():
    random.seed()
    message = random.choice(["Think, captian. Think!",
                                "Might be helpful to THINK that over",
                                "Think carefully about what you need to do..."])

    parsed = parse_for_slowprint(message, "think")

    slow_print_sequence(parsed)

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
        if len(match) >= 2:
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
        slow_print(message=message, wait=0.05) #TODO: make this aesthetic

    style:str = "green" 
    if ship.is_dead():
        style = "bold white on red"
    
    slow_print("GAME OVER", style=styles['default'])
    slow_print(f"Points: {ship.points}", style=styles['default'])

if __name__ == "__main__":
    main()