from collections.abc import Callable
import sys
from typing import List, TypeVar
from ANSI import ANSIColors, ANSICursor
from classes import Cell

COLUMN_WIDTH = 1
DARK = ANSIColors.WHITE + ANSIColors.BG_BLACK
LIGHT = ANSIColors.BLACK + ANSIColors.BG_WHITE


def calculate_spacing(i: int) -> str:
    return ' ' * (1 + COLUMN_WIDTH - len(str(i)))


old_terminal_size = None


class Renderer():
    """
        Renders both the board and instructions onto the screen.
        All methods within this class should be static.
    """
    @staticmethod
    def print_board(board: List[List[Cell]], clear_prompt=True):
        """
            Prints the board centered on the screen. It may or may not clear
            the prompt, based on the clear_prompt parameter.

            If the terminal size has changed, it erases the screen so that the
            rendering is not broken.
        """
        size = len(board)
        spacing = (" " * COLUMN_WIDTH)

        # Clear screen and reset cursor
        global old_terminal_size
        term_size = ANSICursor.get_terminal_size()
        if old_terminal_size != term_size:
            ANSICursor.clear_screen()
            old_terminal_size = term_size
        ANSICursor.move_cursor(term_size.lines // 2 - size + 1,
                               term_size.columns // 2 -
                               (size * 2 + 2 + len(spacing)) // 2)


        # Header row
        header = LIGHT + "0 " + spacing
        for i in range(size):
            header += f"{i + 1}{calculate_spacing(i + 1)}"
            pass
        header += ANSIColors.RESET
        print(header)

        # Board rows
        for i, row in enumerate(board):
            # Center row
            ANSICursor.move_cursor(term_size.lines // 2 - size + 1 + i + 1,
                                   term_size.columns // 2 -
                                   (size * 2 + 2 + len(spacing)) // 2)
            # Print row
            builder = ""
            for c in row:
                builder += spacing + str(c)
            builder += spacing
            print(f"{LIGHT}{i + 1}"
                  + calculate_spacing(i + 1)
                  + f"{DARK}{builder}{ANSIColors.RESET}")

        # Reset prompt
        if clear_prompt:
            ANSICursor.clear_from_row(term_size.lines // 2 + (size + 1) // 2 + 1)


    T = TypeVar('T')
    @staticmethod
    def print_prompt(printer: Callable[..., T],
                     warning: str = "") -> T:
        """
            Calls printer after moving the cursor to the prompt position.
            It also prints 'warning' above priner.
        """
        # Infer requirements
        term_size = ANSICursor.get_terminal_size()

        # Calculate end of board
        first_line = term_size.lines // 2 + 2

        # Erase old prompt
        ANSICursor.clear_from_row(first_line)

        # Render warning right below the board
        ANSICursor.move_cursor(first_line + 1, 0)
        print(warning)

        # Render main prompt
        ANSICursor.move_cursor(first_line + 3, 0)
        try:
            return printer()
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            sys.exit()


    @staticmethod
    def print_message(message: str) -> None:
        """
            Prints a message below the board.
        """
        # Infer requirements
        term_size = ANSICursor.get_terminal_size()

        # Calculate end of board
        first_line = term_size.lines // 2 + 2

        # Erase old prompt
        ANSICursor.clear_from_row(first_line)

        # Render warning right below the board
        ANSICursor.move_cursor(first_line + 1, 0)
        print(message)


    @staticmethod
    def fullscreen_prompt(printer: Callable):
        """
            Calls printer after clearing the board and wait for user input.
        """
        ANSICursor.clear_screen()
        ANSICursor.move_cursor(0, 0)
        printer()
        input("¡Enter para volver al juego!")
        ANSICursor.clear_screen()
