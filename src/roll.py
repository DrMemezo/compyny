import random


def roll(__depth=0, **kwargs:dict[str: int]) -> str:
    """Takes in keyword *INTEGER* parameters and returns the result from a percentege chance."""
    if __depth > 5: # Base case
        RecursionError("No Value Selected for 5 iterations...")
    
    if __depth == 0: # Validation
        val_res = round(sum(kwargs.values()), 1)
        if val_res != 100.0: # Validation
            msg = f"Sum of Values {val_res} given do not add upto 100"
            ValueError(msg)

    
    sorted_kwargs = {key:val for key, val in sorted(kwargs.items(), key=lambda elem: elem[1])}
    chance = random.randint(1,100)
    previous = 0
    for rarity in sorted_kwargs.keys():
        now = previous + sorted_kwargs[rarity]
        if previous < chance <= now:
            return rarity
        else:
            previous = now
    
    return roll(__depth=__depth+1, **kwargs)

class Chance:
    """A Class which represents probabilities"""
    def __init__(self, **kwargs:dict) -> None:
        if not all(map(lambda x: isinstance(x, (int, float)),
                        kwargs.values())):
            raise ValueError("Values given were not all int/float") 
        
        if len(kwargs) < 2:
            raise ValueError("Less than 2 kwargs given")
        
        self.BASE:dict[float|int] = kwargs.copy()
        self.MODIFIED = self.BASE.copy()
        self.update()
        self.needs_update = False
    
    def update(self) -> None:
        """Returns a dict in which all the values inside sum upto 0"""
        divisor:int|float = sum(self.MODIFIED.values())
        
        self.WORKING = {key: ((value / divisor) * 100) 
                        for key, value in self.MODIFIED.items()}
    
    def roll(self) -> str:
        if self.needs_update:
            self.update()
        
        return roll(**self.WORKING)

    def add_to(self, **kwargs) -> None:
        """Increases the probabilty of an event"""
        
        for key, val in kwargs.items():
            try:
                self.MODIFIED[key] += val
            except KeyError:
                raise KeyError("Erroneous input given to 'add_to'")
        self.needs_update = True

    def reset(self, *args) -> None:
        """Resets the probabilty of an event"""
        for key in args:
            self.MODIFIED[key] = self.BASE[key]
        
        self.needs_update = True
