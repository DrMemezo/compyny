
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
    def __init__(self,rarity:str, name:str, value:int) -> None:
        super().__init__(rarity)
        self.name = name
        self.value = value 

    def info(self):
        return (self.name,self.value)
    
    def get_info(self):
        values = self.info()
        return f"{values[0].title()} has a value of {values[1]}"
        

    
    def unique_event():
        """If any scrap is unique from the rest, they can use this module"""
        pass
