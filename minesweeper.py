from collections import deque
from typing import Any, Callable, List
from classes import Action, Cell
import random
import time
from Not_completely_mine.AI import MinesweeperAI
import copy

from renderer import Renderer
ATTEMPTS = 100000


class Minesweeper:
    board: List[List[Cell]] = []
    size: int
    mines: int
    solveable: bool


    def __init__(self, size: int, mines: int):
        """
            Initializes the game and creates a solveable board, if possible.

            WARNING: This class may take a long time to initialize, as it may
            need to create 100000 boards to check for solveability. it also
            erases and rewrites the terminal screen.
        """
        self.size = size
        self.mines = mines
        self.solveable = False
        for i in range(ATTEMPTS):
            self.__prepare_board()
            self.reveal_help(auto_neighbours=False)
            cp = copy.deepcopy(self)
            if winnable(cp):
                self.solveable = True
                break
            elif i % 100 == 0:
                Renderer.print_board(cp.board, clear_prompt=False)
                Renderer.print_message(
                    f"Generando tablero{'.' * (i % 3000 // 1000 + 1)}\n" +
                    f"Intento {i} de {ATTEMPTS}." +
                    f"{i / ATTEMPTS * 100: 5.1f}%"
                )
        # This way it looks pretty
        if self.solveable:
            self.__animate_start()

    def __animate_start(self):
        """
            This function should only be called at the beginning of a solveable
            game. It rediscovers the safe cell but animated this time.
        """
        # This is pretty dumb but it gets the job done
        size = len(self.board)
        for i in range(size):
            for j in range(size):
                if self.board[i][j].discovered:
                    self.discover_neighbours(i, j)
                    return


    def mined(self, y, x):
        """
            Añado esta función únicamente para complir con los requisitos del
            pdf.
            No utilizar.
        """
        return self.board[y][x].is_mine



    def __prepare_board(self):
        self.board = [[Cell() for _ in range(self.size)] for _ in range(self.size)]
        for _ in range(self.mines):
            while True:
                x, y = random.randint(0, self.size - 1), \
                    random.randint(0, self.size - 1)
                cell = self.board[y][x]
                if not cell.is_mine:
                    cell.is_mine = True
                    break
        for i in range(self.size):
            for j in range(self.size):
                self.set_cell_value(i, j)


    def set_cell_value(self, i: int, j: int):
        for row in range(i - 1, i + 2):
            if row < 0 or row > self.size - 1:
                continue
            for column in range(j - 1, j + 2):
                if column < 0 or column > self.size - 1:
                    continue
                if self.board[row][column].is_mine:
                    self.board[i][j].value += 1


    def won(self) -> bool:
        n = 0
        for row in self.board:
            for c in row:
                n += c.discovered
        return n + self.mines == self.size ** 2


    def show_board(self):
        for row in self.board:
            for cell in row:
                if cell.is_mine:
                    cell.discovered = True


    def act(self, action: Action, row: int, column: int) -> str:
        row = row - 1
        column = column - 1
        cell = self.board[row][column]

        # TRY
        if action == Action.TRY:
            if cell.flagged:
                warning = ("No se puede investigar una celda con bandera. " +
                           f"Ejecuta flag {column + 1} {row + 1} para desmarcarla.")
                return warning
            cell.discovered = True
            if cell.value == 0:
                self.discover_neighbours(row, column)

        # FLAG
        elif action == Action.FLAG:
            if cell.discovered:
                return f"¡La celda {column + 1} {row + 1} ya está descubierta!"
            cell.flagged = not cell.flagged

        # EXPAND
        elif action == Action.EXPAND:
            flags = self.neighbouring_flags(row, column)
            fog = self.neighbouring_fog(row, column)
            if (
                cell.discovered
                and cell.value != 0
                and (
                    fog + flags == cell.value
                    or flags == cell.value
                )
            ):
                # If any flags are wrong, lose the game
                if self.neighbouring_correct_flags(row, column) != flags:
                    self.expand_lose(row, column)
                    return ""
                self.clear_safes(row, column)
            else:
                return "Celda inválida"
        return ""


    def expand_lose(self, row: int, column: int):
        self.execute_around(row, column, \
                            self.discover)


    def discover(self, row: int, column: int):
        self.board[row][column].discovered = True




    def help(self) -> bool:
        size = len(self.board)
        output = True
        while True:
            # Initialize knowledge base
            ai = MinesweeperAI(size)
            for i in range(size):
                for j in range(size):
                    cell = self.board[i][j]
                    if cell.discovered:
                        ai.add_knowledge((i, j), cell.value)

            # Reveal cell if necessary
            if ai.make_safe_move() == None and not self.won():
                self.reveal_help()
                output = False
            else:
                break
        return output


    def reveal_help(self, auto_neighbours=True):
        size = len(self.board)
        rand = random.randint(0, size ** 2 - self.mines)
        n = -1
        while True:
            # For each cell
            for i in range(size):
                for j in range(size):
                    cell = self.board[i][j]
                    # Randomly reveal it if it's undiscovered and not a mine
                    if not (cell.discovered or cell.is_mine):
                        n += 1
                        if n == rand:
                            cell.discovered = True
                            if cell.value == 0 and auto_neighbours:
                                self.discover_neighbours(i, j)
                            return



    def count_fog(self) -> int:
        n = 0
        for i in self.board:
            for cell in i:
                if not cell.discovered:
                    n += 1
        return n


    def discover_neighbours(self, row: int, column: int, animated=True):
        """
            I was assisted throughout the troubleshooting of this algorithm by
            Phind. It also taught me about the existance of 'deque's.
            
            This algorithm reveals all obvious cells to prevent the user from
            having to input 8 commands each time they encounter a zero cell.
            It does so through layered and staggered Breadth First Search,
            meaning that it kinda reveals them by path distance from the
            starting point, in order to show a satisfying animation.
        """
        queue = deque([(row, column)])

        while queue:
            if animated:
                time.sleep(0.03)
            for _ in range(len(queue)):
                row, column = queue.popleft()
                for r in range(row - 1, row + 2):
                    for c in range(column - 1, column + 2):
                        # Skip the cell if r or c is out of bounds
                        if not (0 <= r < self.size) or not (0 <= c < self.size):
                            continue

                        cell = self.board[r][c]

                        # Skip the cell if it's the current cell, discovered, or a mine
                        if (r == row and c == column) or cell.discovered or cell.is_mine:
                            continue

                        cell.discovered = True

                        # If the cell value is 0, append it to the queue
                        if cell.value == 0:
                            queue.append((r, c))

            Renderer.print_board(self.board)


    def neighbouring_fog(self, row: int, column: int) -> int:
        return self.count_around(row, column,
                                 lambda row, column: \
                                 not self.board[row][column].discovered
                                 and not self.board[row][column].flagged)


    def neighbouring_flags(self, row: int, column: int) -> int:
        return self.count_around(row, column,
                                 lambda row, column: \
                                 self.board[row][column].flagged)


    def neighbouring_correct_flags(self, row: int, column: int) -> int:
        return self.count_around(row, column,
                                 lambda row, column: \
                                 self.board[row][column].flagged
                                 and self.board[row][column].is_mine)


    def clear_safes(self, row: int, column: int):
        """
            Clears all safe cells around a cell, and flags the mined ones.
        """
        for r in range(row - 1, row + 2):
            if r < 0 or r > self.size - 1:
                continue
            for c in range(column - 1, column + 2):
                if c < 0 or c > self.size - 1:
                    continue
                cell = self.board[r][c]
                if cell.is_mine:
                    cell.flagged = True
                    continue
                cell.discovered = True
                if cell.value == 0:
                    self.discover_neighbours(r, c)


    def count_around(self,
                     row: int,
                     column: int,
                     f: Callable[[int, int], bool]):
        """
            Checks all the neighbouring cells against f and returns the count of
            True returns.
        """
        n = 0
        for r in range(row - 1, row + 2):
            if not (0 <= r < self.size):
                continue
            for c in range(column - 1, column + 2):
                if (
                    not (0 <= c < self.size)
                    or (r == row and c == column)
                ):
                    continue
                n += f(r, c)
        return n


    def execute_around(self,
                       row: int,
                       column: int,
                       f: Callable[[int, int], Any]):
        """
            Execute the passed function on all neighbouring cells
        """
        for r in range(row - 1, row + 2):
            if not (0 <= r < self.size):
                continue
            for c in range(column - 1, column + 2):
                if (
                    not (0 <= c < self.size)
                    or (r == row and c == column)
                ):
                    continue
                f(r, c)


    def lost(self) -> bool:
        if not self.board:
            return False
        for i in self.board:
            for j in i:
                if j.discovered and j.is_mine:
                    return True
        return False

def winnable(game: Minesweeper) -> bool:
    """
        Returns whether a board is winnable. This function alters the original
        parameter.
    """
    size = len(game.board)

    # A game that's won from the begginning is pointless
    if game.won():
        return False

    # Initialize knowledge base
    ai = MinesweeperAI(size)
    for i in range(size):
        for j in range(size):
            cell = game.board[i][j]
            if cell.discovered:
                ai.add_knowledge((i, j), cell.value)
    for _ in range(size ** 2):
        # Make a move
        move = ai.make_safe_move()
        if move == None:
            if game.won():
                return True
            else:
                return False
        cell = game.board[move[0]][move[1]]
        cell.discovered = True
        if not ai.add_knowledge_safe(move, cell.value):
            return False
    return False
