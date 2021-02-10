import pygame as pg
from predicates import * 
from random import randint, random, choices
from platforms.desktop.desktop_handler import DesktopHandler
from specializations.dlv2.desktop.dlv2_desktop_service import DLV2DesktopService
from languages.asp.asp_mapper import ASPMapper
from languages.asp.asp_input_program import ASPInputProgram
import os
from time import sleep
import datetime
from threading import Thread, RLock, Condition
from copy import deepcopy
import itertools

FAIR = 1
UNFAIR = 1

class MementoHandler:
    pass

class SpriteMap:
    def __init__(self,DIM):
        self.DIM = DIM
        self._sprites = {}
        self._cell = []
        for sym in range(1,13):
            for col in range(1,9):
                self.set(sym,col,self._load_tile(self._get_tile_filename(sym, col)))

        self.set(0,0,self._load_tile(self._get_tile_filename(0,0)))     #blank
        self.set(-1,0,self._load_tile(self._get_tile_filename(-1,0)))   #skullbomb

        self._cell.append(self._load_tile("artworks/lead.png")) 
        self._cell.append(self._load_tile("artworks/gold.png")) 

        self._home = pg.image.load("artworks/homescreen.png")
        self._background = pg.image.load("artworks/background.png")
    
    def _load_tile(self,imagename) -> 'Surface':
        return pg.transform.scale(pg.image.load(imagename), (self.DIM,self.DIM))

    def _get_tile_filename(self, x, y) -> str:
        if x == 0 or x == -1:
            y = 0
        return "artworks/{}-{}.png".format(x, y)
    
    def _build_name(self, sym, col):
        return "{}-{}".format(sym,col)
    
    def get(self,sym,col):
        return self._sprites[self._build_name(sym,col)]

    def set(self,sym,col,val):
        self._sprites[self._build_name(sym,col)] = val

    def get_cell(self, i : int):
        return self._cell[i]

    def get_home(self):
        return self._home
    
    def get_bg(self):
        return self._background
        

class UrgentLock:
    def __init__(self):
        self._lock = RLock()
        self._condition = Condition(self._lock)
        self._urgent = False
        self._locked = False
    
    def acquire(self):
        with self._lock:
            while self._urgent or self._locked:
                self._condition.wait()
            self._locked = True
    
    def urgent_acquire(self):
        with self._lock:
            self._urgent = True
            while self._locked:
                self._condition.wait()
            self._locked = True
    
    def release(self):
        with self._lock:
            self._locked = False
            self._condition.notify_all()

    def urgent_release(self):
        with self._lock:
            self._urgent = False
            self.release()


class Board:

    def __init__(self, size:int):
        self.size = size
        self._board = [[EmptyCell(x,y,0) for y in range(self.size)] for x in range(self.size)]
        self._row_counter = [0 for i in range(self.size)]
        self._col_counter = [0 for i in range(self.size)]
        self._incomplete_counter = self.size*self.size

    def get_element(self, x: int, y: int) -> 'Predicate':
        return self._board[x][y]

    def get_size(self) -> int:
        return self.size

    def add_rune(self, in_rune: InputRune, sol: Solution) -> int:
        """gets a solution from Game and returns the amount of points"""
        points = 0

        if sol != None:
            points = 1

            x = int(sol.get_posx())
            y = int(sol.get_posy())

            if (in_rune.get_rune_type() == -1):
                self._row_counter[x] -= 1
                self._col_counter[y] -= 1
                points += 2 if self._board[x][y].get_rune_type() == 0 else 4

                self._board[x][y] = BusyCell(x, y, -1, 0, 1)

                sleep(0.35)

                self._board[x][y] = EmptyCell(x, y, 1)
                
            else:
                """if the new position is not already completed, points stonkssss pew pew"""
                if self._board[x][y].get_completed() == 0:
                    points += 4
                    self._incomplete_counter -= 1

                self._board[x][y] = BusyCell(x, y, in_rune.get_rune_type(), in_rune.get_color(), 1)

                """counters go brrrrrr"""
                self._row_counter[x] += 1
                self._col_counter[y] += 1
            
        return points

    def compute_board(self, sol: Solution) -> int:
        points = 0

        x = int(sol.get_posx())
        y = int(sol.get_posy())

        row_to_clear = False
        col_to_clear = False

        if self._row_counter[x] == self.size:
            row_to_clear = True
                
        if self._col_counter[y] == self.size:
            col_to_clear = True
                
        if row_to_clear:
            self._row_counter[x] = 0
            for i in range(self.size):
                self._board[x][i] = EmptyCell(x,i,1)
                self._col_counter[i] -= 1 if self._col_counter[i] > 0 else 0
            points += self.size
            
        if col_to_clear:
            self._col_counter[y] = 0
            for i in range(self.size):
                self._board[i][y] = EmptyCell(i,y,1)
                self._row_counter[i] -= 1 if self._row_counter[i] > 0 else 0
            points += self.size

        return points        

    def is_clear(self) -> bool:
        for i in range(self.size):
            if self._row_counter[i] != 0:
                return False
        
        return True
    
    def end(self) -> bool:
        return self._incomplete_counter == 0
    
    def can_be_placed(self, in_rune: InputRune) -> bool:
        if in_rune.get_rune_type() > 0:
            for i,j in itertools.permutations(range(self.size), r=2):
                if  isinstance(self._board[i][j],EmptyCell) and \
                    self._check_neighbors(i,j,in_rune):
                    return True
            return False
        return True
    
    def _check_neighbors(self, x, y, in_rune: InputRune) -> bool:
        c = 0
        lis = [
            (min(0,x-1),y),
            (min(self.size-1,x+1),y),
            (x,min(0,y-1)),
            (x,min(self.size-1,y+1)),
            ]
        for i,j in lis:
            if isinstance(self._board[i][j], BusyCell):
                c += 1
                typ = self._board[i][j].get_rune_type()
                col = self._board[i][j].get_color()
                if typ > 0 and not (typ == in_rune.get_rune_type() or typ == in_rune.get_color()):
                    return False
        return c > 0

class Game(Thread):
    """Central class for handling most of the game logic"""
    MAXLIFEPOINTS = 4

    def __init__(self, difficulty=1):
        super().__init__()
        """constructor, should create an empty board, having size dependant by difficulty"""
        self._running = False
        # self._board = Board(difficulty * 2 + 7)
        self._board = Board(9)
        self._runes = 6 + (difficulty * 2)
        self._colors = 2 + (difficulty * 2)
        self._points = 0
        self._lives = Game.MAXLIFEPOINTS
        self._dlv_handler = AlchemyDLVHandler()
        self._in_rune = None
        self._lock = UrgentLock()
        self._step = False
        self._memento_handler = MementoHandler(self)
        self.weights = [
            1, #Blank rune
            0 #Skull bomb
        ]
        self.weights.append(100 - sum(self.weights))
        self.pop = [
            InputRune(0,0),
            InputRune(-1,0),
            None
        ]


    def get_points(self) -> int:
        return self._points

    def get_lives(self) -> int:
        return self._lives

    def get_board(self) -> Board:
        return self._board
    
    def get_in_rune(self):
        return self._in_rune

    def set_points(self, points: int):
        self._points = points

    def set_lives(self, lives: int):
        self._lives = lives

    def set_board(self, board: Board):
        self._board = board
    
    def set_in_rune(self, in_rune: InputRune):
        self._in_rune = in_rune

    def is_running(self) -> bool:
        return self._running

    def flip_running(self) -> None:
        self._lock.urgent_acquire()
        self._running = not self._running
        self._lock.urgent_release()

    def is_alive(self) -> bool:
        return self._lives > 0

    def step(self) -> None:
        self._step = True
    
    def run(self) -> None:
        while self.is_alive():
            self._lock.acquire()
            if self._running:
                self._proceed()
                self._sleep()
            if self._step:
                self._step = False
                self._proceed()
            self._lock.release()
    
    def _generate_rune(self):
        if self._board.is_clear():
            self._in_rune = InputRune(0,0)
        else:
            self._in_rune = choices(self.pop, self.weights)[0]             
            while self._in_rune == None or (not self._board.can_be_placed(self._in_rune) and random() > 0.5):
                self._in_rune = InputRune(randint(1, self._runes), randint(1, self._colors))
            #debugging
            if not self._board.can_be_placed(self._in_rune):
                global UNFAIR 
                UNFAIR += 1
            else:
                global FAIR 
                FAIR += 1
            

    def _proceed(self) -> None:
        if self._in_rune is None:
            self._generate_rune()

        self._memento_handler.save()

        self._sleep()
        sol = self._dlv_handler.get_solution(self._in_rune, self._board, self._lives)
        self._sleep()
        
        if sol == None:
            self._sleep()
            self._lives -= 1 
            self._in_rune = None
        else:
            self._points += self._board.add_rune(self._in_rune, sol)
            self._in_rune = None
            #display the board with the added rune
            self._sleep()
            p = self._board.compute_board(sol)
            if p > 0:
                self.lives = Game.MAXLIFEPOINTS
            self._points += p

            self._lives = min(self._lives + 1, Game.MAXLIFEPOINTS)
            #display the board with the changes implied by the added rune (points and removals)

            if self._board.end(): #TODO gamemode endless // complete board
                self._sleep(5)
                self._lives = 0


    def _sleep(self, time = 0):
        sleep(time)

    def rollback(self):
        self._running = False
        self._step = False
        self._memento_handler.restore()


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
        self.input_program = ASPInputProgram()
        self.input_program.add_files_path("alchemy.dlv2")
        self.countlogs = 0

    def log_program(self):
        if self.countlogs == 0:
            timestamp = datetime.datetime.now()
            self.dir = f"{timestamp.hour}-{timestamp.minute}-{timestamp.second}"
            os.mkdir(f"logs/{self.dir}")
        with open(f"logs/{self.dir}/alchemy-{self.countlogs}.log","w") as f:
            f.write(self.input_program.get_programs())
        self.countlogs+=1
    
    def _change_files(self, in_rune: InputRune):
        self.input_program.clear_files_paths()
        self.input_program.add_files_path("common.dlv2")
        if in_rune.get_rune_type() != -1:
            self.input_program.add_files_path("commonrunes.dlv2")
            if in_rune.get_rune_type() == 0:
                self.input_program.add_files_path("blank.dlv2")
            else:
                self.input_program.add_files_path("rune.dlv2")
        else:
            self.input_program.add_files_path("skullbomb.dlv2")

    def get_solution(self, in_rune: InputRune, board: Board, life_points: int) -> 'Solution':
        self._change_files(in_rune)
        
        size = board.get_size()
        for i in range(size):
            for j in range(size):
                self.input_program.add_object_input(board.get_element(i,j))
        
        self.input_program.add_object_input(SizeOfMatrix(size))
        self.input_program.add_object_input(in_rune)
        self.input_program.add_object_input(LifePoints(life_points))

        self._handler.add_program(self.input_program)
        

        self.log_program()
        answer_sets = self._handler.start_sync()

        self._handler.remove_all()
        self.input_program.clear_programs()
        try:
            for ass in answer_sets.get_optimal_answer_sets():
                for atom in ass.get_atoms():
                    if isinstance(atom, Solution):
                        print(atom)
                        return atom
        except Exception as e:
            print(str(e))
            return None

        print('none')
        return None



class AlchemyGUI:
    HOMESIZE = (640,640)
    TICKRATE = 60
    DIM = 60
    OFFSET = 50
    

    def __init__(self):
        pg.init()
        self._sprites = SpriteMap(self.DIM)
        self._clock = pg.time.Clock()
        self._ourfont_small = pg.font.Font(pg.font.get_default_font(),15)
        self._ourfont_large = pg.font.Font(pg.font.get_default_font(),25)
        self._text = ""
        self._current_difficulty = 1
        self._game = None
        # self._screen = pg.display.set_mode(self.HOMESIZE)
        pg.display.set_caption("Poor man's Alchemy")
        
    def set_game(self, game: Game) -> None:
        self._game = game
        self._len = self._game.get_board().get_size() * self.DIM + self.OFFSET * 2
        self._screen = pg.display.set_mode((self._len,self._len))
        self._game.start()

    
    def _render_text(self, text: str, isLarge=False, color=(0,0,0)) -> 'Surface':
        if isLarge:
            return self._ourfont_large.render(text,True,(0,0,0))
        return self._ourfont_small.render(text,True,(0,0,0))

    def run(self):
        while True:
            self._clock.tick(self.TICKRATE)
            self.event_handler()
            if self._game == None:
               self.draw_home()
            else:
                self.draw_game()

    def draw_home(self) -> None:
        self._screen = pg.display.set_mode(self.HOMESIZE)
        self._screen.blit(self._sprites.get_home(), (0,0))
        self._screen.blit(self._render_text("Difficulty: {} ".format(self._current_difficulty)), (280,260))
        self._screen.blit(self._render_text("Press space to change, or enter to start."), (180,300))
        pg.display.flip()

    def draw_game(self) -> None:
        self._screen.blit(self._sprites.get_bg(), (0,0))

        if self._game.is_alive():
            for i in range(self._game.get_board().get_size()):
                for j in range(self._game.get_board().get_size()):
                    elem = self._game.get_board().get_element(i,j)
                    y = i * self.DIM + self.OFFSET
                    x = j * self.DIM + self.OFFSET
                    comp = 0 if elem.get_completed() == 0 else 1
                    self._screen.blit(self._sprites.get_cell(comp), (x,y))
                    
                    if not elem.is_empty():
                        self._screen.blit(self._sprites.get(elem.get_rune_type(),elem.get_color()), (x,y))
        
            self._screen.blit(self._render_text("{} points".format(self._game.get_points())), (0,0))
            self._screen.blit(self._render_text("{} lives".format(self._game.get_lives())), (self._len - self.OFFSET,0))

            in_rune = self._game.get_in_rune()
            if in_rune != None:
                self._screen.blit(self._sprites.get(in_rune.get_rune_type(),in_rune.get_color()), (self._len / 2 - self.DIM/2, 0))
        else:
            print("finito")
            sleep(5)
            if self._game.get_board().end():
                self._text = "You win!"
            else:
                self._text = "Game Over!"
        
            self._screen.blit(self._render_text(self._text, True), (self._len / 2 - self.OFFSET, self._len/2 - self.OFFSET))
            self._screen.blit(self._render_text("{} points".format(self._game.get_points())), (self._len / 2 - self.OFFSET, self._len/2))
            self._screen.blit(self._render_text("press N to play again"), (self._len / 2 - self.OFFSET, self._len/2 + self.OFFSET))
        
        pg.display.flip()

    def event_handler(self) -> None:
        """handling keyboard events"""
        for event in pg.event.get():
            if event.type == pg.constants.QUIT:
                global FAIR
                global UNFAIR
                print(f"Fair {FAIR}\nUnfair {UNFAIR}")
                pg.quit()
                exit()
            elif event.type == pg.constants.KEYDOWN:
                if self._game == None:
                    if event.key == pg.constants.K_SPACE:
                        self._current_difficulty %= 3
                        self._current_difficulty += 1
                    elif event.key == pg.constants.K_RETURN:
                        self.set_game(Game(self._current_difficulty))
                else:
                    if event.key == pg.constants.K_n:
                        self._game = None
                    elif not self._game.is_alive():
                        continue
                    elif event.key == pg.constants.K_SPACE:
                        self._game.flip_running()
                    elif event.key == pg.constants.K_RETURN and not self._game.is_running():
                        self._game.step()
                    elif event.key == pg.constants.K_BACKSPACE and not self._game.is_running():
                        self._game.rollback()
        
class MementoHandler:
    def __init__(self,g:Game):
        self._game = g
        self._boards = []
        self._points = []
        self._lives = []
        self._in_runes = []

    def save(self):
        self._boards.append(deepcopy(self._game.get_board()))
        self._points.append(self._game.get_points())
        self._lives.append(self._game.get_lives())
        self._in_runes.append(self._game.get_in_rune())

    def restore(self):
        self._game.set_board(self._boards.pop())
        self._game.set_points(self._points.pop())
        self._game.set_lives(self._lives.pop())
        self._game.set_in_rune(self._in_runes.pop())



if __name__ == '__main__':
    a = AlchemyGUI()
    a.run()
