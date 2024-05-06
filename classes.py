import random



class Ship:
    pass


class Event:
    """Event occurs when the player progresses to another room
        They have a rarity type, and the probability of an event occuring is linked to that type"""
    
    def __init__(self, rarity:str) -> None:
        if rarity not in ["common", "uncommon", "rare"]:
            raise ValueError("unsupported rarity")
        pass

class Scrap(Event):
    """Scraps are basically an event which occurs when a user walks into a new room
    They have a monetary value based on their rarity type"""
    def __init__(self,rarity:str) -> None:
        super().__init__(rarity)
        match rarity: # Get a value for the scrap based on the rarity
            case 'rare':
                self.value = random.randint(200,250)
                self.name = random.choice(["Block O' Gold","Reactor core","True rolex watch"])
            case 'uncommon':
                self.value =  random.randint(135, 185)
                self.name = random.choice(["Candlestick","Airhorn","Rubiks Cube"])
            case 'common':
                self.value = random.randint(50, 100)
                self.name = random.choice(["Fake rolex watch","May/June 2024 Maths paper","disapproving skull"])
    
    def __str__(self) -> str:
        return random.choice([
            f"Despite the overwhelming darkness... you find a {self.name}",
            f"A {self.name} blocks your path...",
            f"How peculiar... a {self.name} lies in front of you..."
        ])

    def inspect(self) -> str:
        return f"{self.name.title()} has a value of {self.value}"
    
    def unique_event():
        """If any scrap is unique from the rest, they can use this module"""
        pass
