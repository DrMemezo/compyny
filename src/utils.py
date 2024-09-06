from rich.console import Console
from time import sleep
from pathlib import Path


CONSOLE = Console()

def get_project_root() -> Path:
    """Gets the /project root directory"""
    path = Path(__file__).resolve().parent.parent
    return path


x = get_project_root()

PATHS = {
    'moons': Path(f'{x}/assets/moons.csv'),
    "rare": Path(f"{x}/assets/scraps/rare.csv"),
    "uncommon": Path(f"{x}/assets/scraps/uncommon.csv"),
    "common": Path(f"{x}/assets/scraps/common.csv"),
    "weapon": Path(f"{x}/assets/scraps/weapons.csv")
}

SFX = {
    "Jester" : {
        "start": Path(f"{x}/assets/sfx/jester-wind-start.mp3"),
        "mild": Path(f"{x}/assets/sfx/jester-wind-mild.mp3"),
        "extreme": Path(f"{x}/assets/sfx/jester-wind-extreme.mp3"),
        "almost": Path(f"{x}/assets/sfx/jester-wind-almost.mp3"),
        "pop": Path(f"{x}/assets/sfx/jester-wind-pop.mp3")
    },
    "attack": Path(f"{x}/assets/sfx/Attack_Player.wav"),
    "hurt": Path(f"{x}/assets/sfx/Damage_sustained.wav"),
    "approach_1": Path(f"{x}/assets/sfx/approach_1.mp3"),
    "approach_2": Path(f"{x}/assets/sfx/approach_2.mp3"),
    "ghost": Path(f"{x}/assets/sfx/ghost_whispers.mp3")
}

def slow_print(message:str, wait:float=0.1,
                style:str="white", end:str="\n"):
    """NOTE: Only pass strings!!"""
    
    if message == "" or message is None: # Does not print whitespaces
        return
    
    global CONSOLE

    for char in message:
        CONSOLE.print(char,style=style, end="")
        sleep(wait)
    print(end=end)    