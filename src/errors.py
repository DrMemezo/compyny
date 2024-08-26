
class RetreatFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoMonsterFlag(BaseException): 
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RunFlag(BaseException): # Runs from a room
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class KilledFlag(BaseException): # Dies via combat
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ProgressFailFlag(BaseException): # Dies via progress fail
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CustomKilledFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class CannotReachFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)