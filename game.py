import pygame as pg
from predicates import * 
from random import randint
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
        self._board = [[EmptyCell(x,y,'0') for y in range(N)] for x in range(N)]
        self._rowCounter = [0 for i in range(N)]
        self._colCounter = [0 for i in range(N)]

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
            if self._board[x][y].get_completed() == '0':
                points += 4

            print(self._board[x][y])

            self._board[x][y] = BusyCell(x, y, inRune.get_typeOfRune(), inRune.get_color(), 1)

            print(self._board[x][y])

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
                self._board[x][i] = EmptyCell(i,y,1)
                self._rowCounter[i] -= 1 if self._rowCounter[i] > 0 else 0
            points += self.size

        """if it didn't clear both row and column, it has to diminish the other one"""
        if rowToClear and not colToClear:
            self._colCounter[y] -= 1

        if not rowToClear and colToClear:
            self._rowCounter[x] -= 1

        return points        

    def is_clear(self) -> bool:
        for i in range(self.size):
            if self._rowCounter[i] != 0:
                return False
        
        return True

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
            with self._lock:
                if self._step:
                    self._step = False
                    self._proceed()

        while(self._running and self._lives > 0):
            with self._lock:
                self._proceed()

    def _proceed(self) -> None:
        #get a random rune inRune
        self._inRune = InputRune(randint(1, self._limit), randint(1, self._limit)) if not self._board.is_clear() else InputRune(0,0)

        self._sleep()
        sol = self._dlvhandler.get_solution(self._inRune, self._board)
        self._sleep()
        
        if sol == None:
            self._sleep()
            self._lives -= 1 
            self._inRune = None
            self._sleep()
        else:
            self._points += self._board.add_rune(self._inRune, sol)
            self._inRune = None
            #display the board with the added rune
            self._sleep()
            self._points += self._board.compute_board(sol)
            #display the board with the changes implied by the added rune (points and removals)
            self._sleep()

    def _sleep(self):
        sleep(0.5)



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

    def get_solution(self, inRune: InputRune, board: Board) -> 'Solution':
        print('dlv')
       
        inputProgram = ASPInputProgram()
        # inputProgram.add_files_path("alchemy.dlv2")
        with open("alchemy.dlv2") as f:
            inputProgram.add_program(f.read())

        f.close()
        
        size = board.get_size()

        for i in range(size):
            for j in range(size):
                inputProgram.add_object_input(board.get_element(i,j))
        
        print(str(size))

        #inputProgram.add_program("sizeOfMatrix(" + str(size) + ").")
        inputProgram.add_object_input(SizeOfMatrix(size))
        inputProgram.add_object_input(inRune)
        #inputProgram.add_program("solution(A,B)?")

        self._handler.add_program(inputProgram)
        #self._handler.add_option("-n 1")

        answerSets = self._handler.start_sync()

        # f = open("test","w")
        # f.write(inputProgram.get_programs())
        # f.close()

        try:
            #for ass in answerSets.get_optimal_answer_sets():
            for atom in answerSets.get_optimal_answer_sets()[0].get_atoms():
                if isinstance(atom, Solution):
                    print(atom)
                    return atom
        except:
            print('xc')
            return None

        self._handler.remove_all()
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
#TODO metodo unico
    def _render_points(self) -> 'Surface':
        return self._ourfont_small.render("Points {}".format(self._game.get_points()),True,(0,0,0))

    def _render_lives(self) -> 'Surface':
        return self._ourfont_small.render("Lives {}".format(self._game.get_lives()),True,(0,0,0))

    def _render_gameover(self) -> 'Surface':
        return self._ourfont_large.render("Game Over!",True,(0,0,0))

    def _render_newgame(self) -> 'Surface':
        return self._ourfont_small.render("press N to play again",True,(0,0,0))

    #def _render_text(self, text, color, isLarge=False):

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
            for i in range(self._board.size):
                for j in range(self._board.size):
                    elem = self._board.get_element(i,j)
                    x = i * DIM + OFFSET
                    y = j * DIM + OFFSET
                    comp = 0 if elem.get_completed() == '0' else 1
                    self._screen.blit(self._cell[comp], (x,y))
                    
                    if not elem.is_empty():
                        self._screen.blit(self._sprites[elem.get_typeOfRune()][elem.get_color()], (x,y))
        
            self._screen.blit(self._render_points(), (0,0))
            self._screen.blit(self._render_lives(), (self._len - OFFSET,0))

            inRune = self._game.get_inRune()
            if inRune != None:
                self._screen.blit(self._sprites[inRune.get_typeOfRune()][inRune.get_color()], (self._len / 2 - DIM/2, 0))

        else:
            self._screen.blit(self._render_gameover(), (self._len / 2 - OFFSET, self._len/2 - OFFSET))
            self._screen.blit(self._render_points(), (self._len / 2 - OFFSET, self._len/2))
            self._screen.blit(self._render_newgame(), (self._len / 2 - OFFSET, self._len/2 + OFFSET))
        
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
