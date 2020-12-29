import pygame as pg
from predicates import * 
from random import randint, random
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from languages.asp.asp_mapper import ASPMapper
from languages.asp.asp_input_program import ASPInputProgram
import os
from time import sleep
from threading import Thread, Lock, Condition

class Board:

    def __init__(self, N: int):
        self.size = N
        self._board = [[EmptyCell(x,y,0) for y in range(N)] for x in range(N)]
        self._rowCounter = [0 for i in range(N)]
        self._colCounter = [0 for i in range(N)]
        self._completed_counter = self.size*self.size

    def get_element(self, x: int, y: int) -> 'Predicate':
        return self._board[x][y]

    def get_size(self) -> int:
        return self.size

    def add_rune(self, inRune: InputRune, sol: Solution) -> int:
        """gets a solution from Game and returns the amount of points"""
        points = 0

        if sol != None:
            points = 1

            x = int(sol.get_posx())
            y = int(sol.get_posy())

            """if the new position is not already completed, points stonkssss pew pew"""
            if self._board[x][y].get_completed() == 0:
                points += 4
                self._completed_counter -= 1

            self._board[x][y] = BusyCell(x, y, inRune.get_typeOfRune(), inRune.get_color(), 1)

            """counters go brrrrrr"""
            self._rowCounter[x] += 1
            self._colCounter[y] += 1
            
        return points

    def compute_board(self, sol: Solution) -> int:
        points = 0

        x = int(sol.get_posx())
        y = int(sol.get_posy())

        rowToClear = False
        colToClear = False

        if self._rowCounter[x] == self.size:
            rowToClear = True
                
        if self._colCounter[y] == self.size:
            colToClear = True
                
        if rowToClear:
            self._rowCounter[x] = 0
            for i in range(self.size):
                self._board[x][i] = EmptyCell(x,i,1)
                self._colCounter[i] -= 1 if self._colCounter[i] > 0 else 0
            points += self.size
            
        if colToClear:
            self._colCounter[y] = 0
            for i in range(self.size):
                self._board[i][y] = EmptyCell(i,y,1)
                self._rowCounter[i] -= 1 if self._rowCounter[i] > 0 else 0
            points += self.size

        return points        

    def is_clear(self) -> bool:
        for i in range(self.size):
            if self._rowCounter[i] != 0:
                return False
        
        return True
    
    def end(self) -> bool:
        return self._completed_counter == 0

class Game(Thread):
    """Central class for handling most of the game logic"""

    def __init__(self, difficulty=1):
        super().__init__()
        """constructor, should create an empty board, having size dependant by difficulty"""
        self._running = False
        self._board = Board(difficulty * 2 + 7)
        self._limit = 3 + difficulty
        self._points = 0
        self._lives = 3
        self._dlvhandler = AlchemyDLVHandler()
        self._inRune = None
        self._lock = Lock()
        self._step = False

    def get_points(self) -> int:
        return self._points

    def get_lives(self) -> int:
        return self._lives

    def get_board(self) -> Board:
        return self._board
    
    def get_inRune(self):
        return self._inRune

    def is_running(self) -> bool:
        return self._running

    def flip_running(self) -> None:
        with self._lock:
            self._running = not self._running

    def is_alive(self) -> bool:
        return self._lives > 0

    def step(self) -> None:
        self._step = True
    
    def run(self) -> None:
        while self.is_alive():
            while self._running and self.is_alive():
                with self._lock:
                    self._proceed()
                self._sleep()
            with self._lock:
                if self._step:
                    self._step = False
                    self._proceed()

    def _proceed(self) -> None:
        #get a random rune inRune
        if random() < 0.1:
            self._inRune = InputRune(0,0)
        else:
            self._inRune = InputRune(randint(1, self._limit), randint(1, self._limit)) if not self._board.is_clear() else InputRune(0,0)

        self._sleep()
        sol = self._dlvhandler.get_solution(self._inRune, self._board)
        self._sleep()
        
        if sol == None:
            self._sleep()
            self._lives -= 1 
            self._inRune = None
        else:
            self._points += self._board.add_rune(self._inRune, sol)
            self._inRune = None
            #display the board with the added rune
            self._sleep()
            self._points += self._board.compute_board(sol)
            self._lives = min(self._lives + 1, 4)
            #display the board with the changes implied by the added rune (points and removals)

            if self._board.end(): #TODO gamemode endless // complete board
                self._lives = 0


    def _sleep(self):
        # sleep(0.5)
        pass



class AlchemyDLVHandler:

    def __init__(self):
        if os.name == 'nt':
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
        self.inputProgram = ASPInputProgram()
        self.inputProgram.add_files_path("alchemy.dlv2")
        self.countlogs = 0

    def log_program(self):
        with open("logs/alchemy-{}.log".format(self.countlogs),"w") as f:
            f.write(self.inputProgram.get_programs())
        self.countlogs+=1


    def get_solution(self, inRune: InputRune, board: Board) -> 'Solution':
        size = board.get_size()
        for i in range(size):
            for j in range(size):
                self.inputProgram.add_object_input(board.get_element(i,j))
        
        self.inputProgram.add_object_input(SizeOfMatrix(size))
        self.inputProgram.add_object_input(inRune)

        self._handler.add_program(self.inputProgram)

        answerSets = self._handler.start_sync()

        self._handler.remove_all()
        # self.log_program()
        self.inputProgram.clear_programs()


        try:
            for ass in answerSets.get_optimal_answer_sets():
                for atom in ass.get_atoms():
                    if isinstance(atom, Solution):
                        print(atom)
                        return atom
        except:
            print('xc')
            return None

        print('none')
        return None


DIM = 60
OFFSET = 50
TICKRATE = 4

class AlchemyGUI:
    
    def __init__(self):
        # super().__init__()
        pg.init()
        self._load_sprites()
        self._clock = pg.time.Clock()
        self._ourfont_small = pg.font.Font(pg.font.get_default_font(),15)
        self._ourfont_large = pg.font.Font(pg.font.get_default_font(),25)
        self._text = ""
        
    def set_game(self, game: Game) -> None:
        self._game = game
        self._board = self._game.get_board()
        self._len = self._board.get_size() * DIM + OFFSET * 2
        self._screen = pg.display.set_mode((self._len,self._len))
        pg.display.set_caption("Poor men's Alchemy")
        self._game.start()

    def _load_sprites(self) -> None:
        self._background = pg.image.load("artworks/background.png")

        self._cell = []
        self._cell.append(self._load_tile("artworks/lead.png")) 
        self._cell.append(self._load_tile("artworks/gold.png")) 
        
        self._sprites = []

        for sym in range(7):
            syms = []
            for col in range(7):
                syms.append(self._load_tile(self._get_tile_filename(sym, col)))
            self._sprites.append(syms)
    
    def _get_tile_filename(self, x, y) -> str:
        if x == 0:
            y = 0
        elif y == 0:
            x = 0
        return "artworks/{}-{}.png".format(x, y)

    def _load_tile(self,imagename) -> 'Surface':
        return pg.transform.scale(pg.image.load(imagename), (DIM,DIM))

    def _render_text(self, text: str, isLarge=False, color=(0,0,0)) -> 'Surface':
        if isLarge:
            return self._ourfont_large.render(text,True,(0,0,0))
        return self._ourfont_small.render(text,True,(0,0,0))

    def run(self):
        while True:
            self._clock.tick(TICKRATE)
            self.event_handler()
            if self._game != None:
               self.draw()
            else:
                print('morto')

    def draw(self) -> None:
        self._screen.blit(self._background, (0,0))

        if self._game.is_alive():
            for i in range(self._board.get_size()):
                for j in range(self._board.get_size()):
                    elem = self._board.get_element(i,j)
                    y = i * DIM + OFFSET
                    x = j * DIM + OFFSET
                    comp = 0 if elem.get_completed() == 0 else 1
                    self._screen.blit(self._cell[comp], (x,y))
                    
                    if not elem.is_empty():
                        self._screen.blit(self._sprites[elem.get_typeOfRune()][elem.get_color()], (x,y))
        
            self._screen.blit(self._render_text("{} points".format(self._game.get_points())), (0,0))
            self._screen.blit(self._render_text("{} lives".format(self._game.get_lives())), (self._len - OFFSET,0))

            inRune = self._game.get_inRune()
            if inRune != None:
                self._screen.blit(self._sprites[inRune.get_typeOfRune()][inRune.get_color()], (self._len / 2 - DIM/2, 0))
        else:
            if self._board.end():
                self._text = "You win!"
            else:
                self._text = "Game Over!"
        
            self._screen.blit(self._render_text(self._text, True), (self._len / 2 - OFFSET, self._len/2 - OFFSET))
            self._screen.blit(self._render_text("{} points".format(self._game.get_points())), (self._len / 2 - OFFSET, self._len/2))
            self._screen.blit(self._render_text("press N to play again"), (self._len / 2 - OFFSET, self._len/2 + OFFSET))
        
        pg.display.flip()

    def event_handler(self) -> None:
        """handling debugging stuff"""
        for event in pg.event.get():
            if event.type == pg.constants.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.constants.KEYDOWN:
                if event.key == pg.constants.K_n:
                    #killa game attuale
                    #chiedi difficoltà
                    diff = 1
                    self.set_game(Game(diff))
                elif not self._game.is_alive():
                    continue
                elif event.key == pg.constants.K_SPACE:
                    self._game.flip_running()
                elif event.key == pg.constants.K_RETURN and not self._game.is_running():
                    self._game.step()

if __name__ == '__main__':
    a = AlchemyGUI()
    a.set_game(Game(1))
    a.run()
