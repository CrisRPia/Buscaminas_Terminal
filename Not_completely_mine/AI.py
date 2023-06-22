import random
import threading


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # If cell is not in the sentence, then no action is necessary.
        if cell not in self.cells:
            return
        
        # If cell is in the sentence, the function should update the sentence
        # so that cell is no longer in the sentence, but still represents a 
        # logically correct sentence given that cell is known to be a mine.
        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # If cell is not in the sentence, then no action is necessary.
        if cell not in self.cells:
            return

        # If cell is in the sentence, the function should update the sentence so
        # that cell is no longer in the sentence, but still represents a 
        # logically correct sentence given that cell is known to be safe.
        self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, size):

        # Set initial size
        self.size = size

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)


    def add_knowledge_safe(self, cell, count, wait=0.5) -> bool:
        """
            Since this task is potentially computationally complex, it may need
            to be cut short, in which case False is returned. Else, True.

            I was also helped by Phind to learn threading in python.
        """

        # Create a wrapper function for add_knowledge to pass the arguments
        def add_knowledge_wrapper():
            self.add_knowledge(cell, count)

        loop_thread = threading.Thread(target=add_knowledge_wrapper)
        loop_thread.start()
        loop_thread.join(wait)

        # Check if the thread is still running after the time limit
        if loop_thread.is_alive():
            # Clean up the thread
            loop_thread.join()
            return False
        return True


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made DONE
            2) mark the cell as safe DONE
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count` DONE
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base DONE
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge DONE
        """
        # 1 and 2
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        # 3
        grid = set()

        # Iterate through all neighboring cells and add them to grid if
        # not already discarded

        # X
        for i in range(-1, 2):
            # Y
            for j in range(-1, 2):
                c = (cell[0] + i, cell[1] + j)
                c_within_range = 0 <= c[0] < self.size and 0 <= c[1] < self.size
                if c != cell and c_within_range and c not in self.safes:
                    if c in self.mines:
                        count -= 1
                    else:
                        grid.add(c)

        # Append the new inferred sentence to knowlege.
        self.knowledge.append(Sentence(grid, count))

        """
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
        """
        changed = True
        while changed:
            # Reset change marker
            changed = False
            
            for i in range(len(self.knowledge)):
                sentence = self.knowledge[i]
                assert isinstance(sentence, Sentence)
                safes = []
                mines = []

                for mine in sentence.known_mines():
                    mines.append(mine)
                    changed = True
                for safe in sentence.known_safes():
                    safes.append(safe)
                    changed = True
                for safe in safes:
                    self.mark_safe(safe)
                for mine in mines:
                    self.mark_mine(mine)
                """
                    5) add any new sentences to the AI's knowledge base
                       if they can be inferred from existing knowledge
                       DONE FINALLY
                """
                for j in range(len(self.knowledge)):
                    if self.knowledge[j] == sentence:
                        break
                    sentence2 = self.knowledge[j]
                    assert isinstance(sentence2, Sentence)

                    # If sentence is a subset of sentence2 (https://stackoverflow.com/questions/16579085/how-can-i-verify-if-one-list-is-a-subset-of-another)
                    if sentence.cells <= sentence2.cells:
                        self.knowledge.append(
                            Sentence(sentence2.cells.difference(
                                    sentence.cells
                                    ),
                                sentence2.count - sentence.count
                                )
                            )

            # Clean empty sets
            temp = []
            for s in self.knowledge:
                if s.cells and s not in temp:
                    temp.append(s)
            self.knowledge = temp

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if not self.safes.difference(self.moves_made):
            return None
        return random.choice(list(self.safes.difference(self.moves_made)))

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
            DONE
        """
        forbidden_moves = self.moves_made.union(self.mines)

        # If no moves are possible, the game's won. Return None
        if len(forbidden_moves) == self.size ** 2:
            return None

        # Else, randomly choose a new move
        while True:
            move = (random.randint(0, self.size - 1), 
                    random.randint(0, self.size - 1))
            if move not in forbidden_moves:
                break
        return move
