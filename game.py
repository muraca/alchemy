import pygame as pg
from predicates import * 
import itertools

class Game:
    """Central class for handling most of the game logic"""

    def __init__(self, N: int):
        """constructor, should create an empty board, having size N*N,
        with correct status given the size of the board"""
        self._running = False
        self._board = Board(N)

    def loop(self) -> None:
        """one loop iteration in the game logic and handling
        this should only contain """
        pass

    def event_handler(self) -> None:
        """handling debugging stuff"""
        pass


class Board:

    def __init__(self, N: int):
        self.size = N
        self._board = [[EmptyCell(x,y,False) for x in range(N)] for y in range(N)]
        self._rowCounter = [0 for i in range(N)]
        self._colCounter = [0 for i in range(N)]

    def getElement(self, x: int, y: int):
        return self._board[x][y]

    def addRune(self, inRune: InputRune, sol: Solution):
        """gets a solution from Game and returns the amount of points"""
        points = 0

        if sol != None:
            points = 1

            x = sol.get_posx
            y = sol.get_posy

            """if the new position is not already completed, points stonkssss pew pew"""
            if self._board[x][y].get_completed == False:
                points += 5

            self._board[x][y] = BusyCell(x, y, inRune.get_typeOfRune, inRune.get_color, True)

            """counters go brrrrrr"""
            self._rowCounter[x] += 1
            self._colCounter[y] += 1

            #TODO fix da qui
            rowToClear = False
            colToClear = False

            if self._rowCounter[x] == self.size:
                rowToClear = True
                
            if self._colCounter[y] == self.size:
                colToClear = True
                
            if rowToClear:
                self.clearRowCol(x,False)
                self._rowCounter[x] = 0
                self._colCounter[i] -= 1 if self._colCounter[i] > 0 for i in range(self.size)
                points += self.size
            
            if colToClear:
                self.clearRowCol(y,True)
                self._colCounter[y] = 0
                self._rowCounter[i] -= 1 if self._rowCounter[i] > 0 for i in range(self.size)
                points += self.size

            """if it didn't clear both row and column, it has to diminish the other cumpari"""
            if rowToClear and not colToClear:
                self._colCounter[y] -= 1

            if not rowToClear and colToClear:
                self._rowCounter[x] -= 1
            #a qui
            #in clearRowCol(x,y) ?
            #yes aspe che provo un attimo
        return points


    def clearRowCol(self, x: int, isCol: bool, isDouble = False):
        main = self._colCounter if isCol else self._rowCounter
        seco = self._rowCounter if isCol else self._colCounter
        for i in range(self.size):
            self._board[x][i] = EmptyCell(x, i, True)
            seco[i] -= 1 if seco[i] != self.size


    def clearRow(self, x: int):
        for i in range(self.size):
            self._board[x][i] = EmptyCell(x, i, True)
            self._colCounter -= 1 #FIXME
        self._rowCounter[x] = 0

    def clearCol(self, y: int):
        for i in range(self.size):
            self._board[i][y] = EmptyCell(i, y, True)
            self._rowCounter -= 1 #FIXME
        self._colCounter[y] = 0

    