
class RetreatFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class NoMonsterFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RunFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class KilledFlag(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)