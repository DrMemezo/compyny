import random

def roll(**kwargs:dict[str: int]) -> str:
    """Takes in keyword *INTEGER* parameters and returns the result from a percentege chance."""
    if sum(kwargs.values()) != 100: # Validation
        raise SyntaxError("All parameters given must add up to 100")
    
    sorted_kwargs = {key:val for key, val in sorted(kwargs.items(), key=lambda elem: elem[1])}
    chance = random.randint(1,100)
    previous = 0
    for rarity in sorted_kwargs.keys():
        now = previous + sorted_kwargs[rarity]
        if previous < chance <= now:
            return rarity
        else:
            previous = now

    raise SyntaxError("All parameters given must add up to 100")