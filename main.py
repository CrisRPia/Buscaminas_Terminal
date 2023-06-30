from typing import Tuple
from classes import Action
from ANSI import ANSICursor
from helpers import *
from minesweeper import Minesweeper
from renderer import Renderer
import icons

game: Minesweeper
COLUMN_WIDTH = 1
MAN = """
Sintaxis: acción coordenada_horizontal coordenada_vertical

Ejemplo: flag 5 5

Posibles acciones:

    flag: Marcar la celda con una bandera. Es útil para recordar las minas ya
          inferidas.

    help: Pedirle ayuda al programa en un movimiento. La IA determinará si es
          posible realizar un movimiento seguro y lo dirá. De no ser posible,
          se desbloquearán celdas hasta que un movimiento seguro sea posible.

    try: Descubre la celda. Si la celda es una mina, el juego se pierde. Si la
         celda no tiene minas vecinas, efectuará try en las celdas vecinas. Esta
         acción se ejecuta por defecto; '5 5' es equivalente a 'try 5 5'. Una
         vez se descubre la última celda sin minas, el juego se gana.

    expand: Al usarse en una celda descubierta con valor numérico, descubre o 
            aplica bandera a las celdas vecinas correctas si el número de 
            celdas vecinas sin descubrir es equivalente al valor de la celda
            electa menos la cantidad de banderas vecinas.
"""


def main():
    global game

    # Set screen
    ANSICursor.show_cursor()
    ANSICursor.clear_screen()
    ANSICursor.move_cursor(0, 0)

    # Set game
    size, mines = get_starters()
    game = Minesweeper(size, mines)

    if not game.solveable:
        warning = "Este tablero no se puede solucionar con seguridad."
    else:
        warning = "Este tablero se puede resolver con seguridad."
    ANSICursor.clear_screen()

    while True:
        Renderer.print_board(game.board)
        while True:
            # Final screen
            if game.lost():
                game.show_board()
                ANSICursor().clear_screen()
                Renderer.print_board(game.board)
                print("\nPerdiste\n")
                ANSICursor.show_cursor()
                return
            elif game.won():
                Renderer.print_board(game.board)
                print("\n¡Ganaste!\n")
                ANSICursor.show_cursor()
                return

            # Main loop
            ANSICursor.show_cursor()
            move = Renderer.print_prompt(
                lambda: input("Acción (man para explicación): "),
                warning=warning
            ).split()
            ANSICursor.hide_cursor()

            # Call each possible action
            inp = ""
            try:
                if move[0] == Action.MAN.value:
                    # The manual must be rendered on a separate page
                    Renderer.print_board(game.board)
                    Renderer.fullscreen_prompt(lambda: print(MAN))
                    Renderer.print_board(game.board)
                    continue
                if move[0] == Action.HELP.value:
                    if game.help():
                        warning = "Es posible inferir un movimiento seguro."
                    else:
                        warning = "No fué posible inferir un movimiento " + \
                            "seguro. Se ha revelado información."
                    break
                if move[0].isdigit():
                    y, x = int(move[0]), int(move[1])
                    assert 0 < x <= size and 0 < y <= size
                    warning = game.act(Action.TRY, x, y)
                    break
                else:
                    y, x = int(move[1]), int(move[2])
                    assert 0 < x <= size and 0 < y <= size
                if move[0] == Action.FLAG.value:
                    warning = game.act(Action.FLAG, x, y)
                    break
                if move[0] == Action.TRY.value:
                    game.act(Action.TRY, x, y)
                    break
                if move[0] == Action.EXPAND.value:
                    warning = game.act(Action.EXPAND, x, y)
                    break
                raise NameError
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    raise e
                warning=f"Sintáxis inválida ({' '.join(move)})."
        ANSICursor.show_cursor()


def get_starters() -> Tuple[int, int]:
    """
        Gets initial board config values.
    """
    size, mines = 0, 0
    while size < 3 or size > 10:
        size = Renderer.print_prompt(
            lambda: ask_int("Tamaño del tablero (de 3 a 10): ")
        )
    ANSICursor.clear_screen()
    while mines < 1 or mines > size ** 2 - 1:
        mines = Renderer.print_prompt(
            lambda: ask_int(f"Cantidad de minas (de 1 a {size ** 2 - 1}" +

                            # 21% is about what's reasonable for a hard game;
                            # we add one because on a 3x3 board recommending
                            # one mine is ridiculous
                            f", se recomiendan {int(size ** 2 * 0.2) + 1}): ")
        )
    ANSICursor.clear_screen()
    return size, mines


if __name__ == "__main__":
    try:
        ANSICursor.clear_screen()
        # Set legacy mode
        if Renderer.print_prompt(
            lambda: input("Modo de legado (Enter vacío para no aplicarlo): "),
        ):
            icons.legacy = True

        # Main loop
        main()
        while True:
            if not input("¿Jugar nuevamente (Enter vacío para 'sí')? "):
                main()
            else:
                break
    except:
        ANSICursor.show_cursor()
        print("\n\n¡Hasta luego!")
