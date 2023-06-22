import os
import sys
"""
    TEXT COLOR  CODE  TEXT STYLE  CODE  BACKGROUND COLOR  CODE
    Black       30    No effect   0     Black             40
    Red         31    Bold        1     Red               41
    Green       32    Underline   2     Green             42
    Yellow      33    Negative1   3     Yellow            43
    Blue        34    Negative2   5     Blue              44
    Purple      35                      Purple            45
    Cyan        36                      Cyan              46
    White       37                      White             47

    Para realizar este archivo me ayudé con Phind. Investigué la tabla en:
        https://www.kaggle.com/general/273188
    y le pedí a la IA que escriba el pasaje a constantes. Podría haberlo hecho
    yo, pero así me ahorro trabajo de esclavo.
"""

class ANSIColors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    NO_EFFECT = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[2m"
    NEGATIVE1 = "\033[3m"
    NEGATIVE2 = "\033[5m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_PURPLE = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    RESET = "\033[0m"


class ANSICursor:
    @staticmethod
    def move_cursor(row, col):
        sys.stdout.write(f"\x1B[{row};{col}H")


    @staticmethod
    def clear_screen():
        sys.stdout.write("\x1B[2J")
        
    @staticmethod
    def get_terminal_size():
        return os.get_terminal_size()


    @staticmethod
    def clear_from_row(row):
        ANSICursor.move_cursor(row, 1)
        sys.stdout.write("\x1B[J")
        sys.stdout.flush()


    @staticmethod
    def hide_cursor():
        sys.stdout.write("\x1B[?25l")
        sys.stdout.flush()

    @staticmethod
    def show_cursor():
        sys.stdout.write("\x1B[?25h")
        sys.stdout.flush()
