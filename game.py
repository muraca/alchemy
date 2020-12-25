import pygame as pg
from predicates import * 
import itertools
from random import randint
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from languages.asp.asp_mapper import ASPMapper
from languages.asp.asp_input_program import ASPInputProgram
import os

class Game:
    """Central class for handling most of the game logic"""

    def __init__(self, difficulty: int):
        """constructor, should create an empty board, having size dependant by difficulty"""
        self._alive = True
        self._running = False
        self._board = Board(difficulty * 2 + 7)
        self._limit = 3 + difficulty
        self._points = 0
        self._lives = 3
        #create a GUI object
        self._dlvhandler = AlchemyDLVHandler()

    def loop(self) -> None:
        """one loop iteration in the game logic and handling
        this should only contain """
        while(self._running and self._alive):
            self._proceed()
            #sleep

    def _proceed(self) -> None:
        #get a random rune inRune
        inRune = InputRune(randint(1, self._limit), randint(1, self._limit)) if not self._board.isClear() else InputRune(0,0)
        #display the inRune
        #sleep
        sol = self._dlvhandler.getSolution(inRune, self._board)
        #sleep
        if sol == None:
            self._lives -= 1 
            if self._lives == 0:
                self._lose()
        else:
            self._points += self._board.addRune(inRune, sol)
            #display the board with the added rune
            #sleep
            self._points += self._board.clearRowCol(sol)
            #display the board with the changes implied by the added rune (points and removals)
            #sleep

    def event_handler(self) -> None:
        """handling debugging stuff"""
        pass
        #if event == n_key
        #newGame ?
        #if not self._alive:
        #break ?
        #if event == space_key:
        #self._running = not self._running
        #elif event == enter_key and not self._running:
        #self._proceed
        

    def _lose(self) -> None:
        pass


class Board:

    def __init__(self, N: int):
        self.size = N
        self._board = [[EmptyCell(x,y,False) for x in range(N)] for y in range(N)]
        self._rowCounter = [0 for i in range(N)]
        self._colCounter = [0 for i in range(N)]

    def getElement(self, x: int, y: int) -> 'Predicate':
        return self._board[x][y]

    def addRune(self, inRune: InputRune, sol: Solution) -> int:
        """gets a solution from Game and returns the amount of points"""
        points = 0

        if sol != None:
            points = 1

            x = sol.get_posx
            y = sol.get_posy

            """if the new position is not already completed, points stonkssss pew pew"""
            if self._board[x][y].get_completed == False:
                points += 4

            self._board[x][y] = BusyCell(x, y, inRune.get_typeOfRune, inRune.get_color, True)

            """counters go brrrrrr"""
            self._rowCounter[x] += 1
            self._colCounter[y] += 1
            
        return points

    def clearRowCol(self, sol: Solution) -> int:
        points = 0

        x = sol.get_posx
        y = sol.get_posy

        rowToClear = False
        colToClear = False

        if self._rowCounter[x] == self.size:
            rowToClear = True
                
        if self._colCounter[y] == self.size:
            colToClear = True
                
        if rowToClear:
            self.clearRowCol(x,False)
            self._rowCounter[x] = 0
            for i in range(self.size):
                self._colCounter[i] -= 1 if self._colCounter[i] > 0 else 0
            points += self.size
            
        if colToClear:
            self.clearRowCol(y,True)
            self._colCounter[y] = 0
            for i in range(self.size):
                self._rowCounter[i] -= 1 if self._rowCounter[i] > 0 else 0
            points += self.size

            """if it didn't clear both row and column, it has to diminish the other one"""
        if rowToClear and not colToClear:
            self._colCounter[y] -= 1

        if not rowToClear and colToClear:
            self._rowCounter[x] -= 1

        return points        

        """
        main = self._colCounter if isCol else self._rowCounter
        seco = self._rowCounter if isCol else self._colCounter
        for i in range(self.size):
            self._board[x][i] = EmptyCell(x, i, True)
            seco[i] -= 1 if seco[i] != self.size else 0"""

    def isClear(self) -> bool:
        for i in range(self.size):
            if self._rowCounter[i] != 0:
                return False

        return True

"""
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
"""

class AlchemyDLVHandler:

    def __init__(self):
        if os.name() == 'nt':
            self._handler = DesktopHandler(DLV2DesktopService("../executable/dlv2.exe"))
        elif os.uname().sysname == 'Darwin':
            self._handler = DesktopHandler(DLV2DesktopService("../executable/dlv2-mac"))
        else:
            self._handler = DesktopHandler(DLV2DesktopService("../executable/dlv2"))

        ASPMapper.get_instance().register_class(InputRune)
        ASPMapper.get_instance().register_class(BusyCell)
        ASPMapper.get_instance().register_class(EmptyCell)
        ASPMapper.get_instance().register_class(SizeOfMatrix)
        ASPMapper.get_instance().register_class(Solution)

    def getSolution(self, inRune: InputRune, board: Board) -> Solution:
        inputProgram = ASPInputProgram()
        inputProgram.add_files_path("alchemy.dlv2")
        
        for i in range(board.size):
            for j in range(board.size):
                inputProgram.add_object_input(board.getElement(i,j))
        
        inputProgram.add_program("Solution(A,B)?")

        self.handler.add_program(inputProgram)
        self._handler.add_option("-n 1")


        answerSets = self.handler.start_sync()
        self._handler.remove_all()

        for atom in answerSets.get_optimal_answer_sets()[0].get_atoms():
            return atom

        return None

