import icons
from ANSI import ANSIColors
from enum import Enum

class Cell():
    def __init__(self, value=0):
        if not (0 <= value <= 8):
            raise ValueError(f"Invalid value {value}. " +
                             "It must be an integer between 0 and 8.")
        self.flagged = False
        self.is_mine = False
        self.discovered = False
        self.value = value


    def __str__(self) -> str:
        if self.flagged:
            return f"{ANSIColors.GREEN}{icons.FLAG[icons.legacy]}"
        if not self.discovered:
            return f"{ANSIColors.WHITE}{icons.FOG[icons.legacy]}"
        if self.is_mine:
            return f"{ANSIColors.RED}{icons.MINE[icons.legacy]}"
        if self.value == 0:
            return f"{ANSIColors.WHITE}{icons.BLANK}"
        return ANSIColors.WHITE + str(self.value)


class Action(Enum):
    MAN = "man"
    HELP = "help"
    FLAG = "flag"
    TRY = "try"
    EXPAND = "expand"
