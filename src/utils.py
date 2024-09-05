from rich.console import Console
from time import sleep
from pathlib import Path


CONSOLE = Console()

PATHS = {
    'moons': Path('assets/moons.csv'),
    "rare": Path("assets/scraps/rare.csv"),
    "uncommon": Path("assets/scraps/uncommon.csv"),
    "common": Path("assets/scraps/common.csv"),
    "weapon": Path("assets/scraps/weapons.csv")
}

SFX = {
    "Jester" : {
        "start": Path(r"assets\sfx\jester-wind-start.mp3"),
        "mild": Path(r"assets\sfx\jester-wind-mild.mp3"),
        "extreme": Path(r"assets\sfx\jester-wind-extreme.mp3"),
        "almost": Path(r"assets\sfx\jester-wind-almost.mp3"),
        "pop": Path(r"assets\sfx\jester-wind-pop.mp3")
    },
    "attack": Path(r"assets\sfx\Attack_Player.wav"),
    "hurt": Path(r"assets\sfx\Damage_sustained.wav"),
    "approach_1": Path(r"assets\sfx\approach_1.mp3"),
    "approach_2": Path(r"assets\sfx\approach_2.mp3"),
    "ghost": Path(r"assets\sfx\ghost_whispers.mp3")
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