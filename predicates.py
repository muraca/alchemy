from languages.predicate import Predicate

class Rune:
    def __init__(self, rune_type = None, color = None ):
        self.rune_type = rune_type
        self.color = color

    def get_rune_type(self):
        return self.rune_type

    def get_color(self):
        return self.color

    def set_rune_type(self, rune_type):
        self.rune_type = rune_type

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return f"{self.rune_type},{self.color}"

class Position:
    def __init__(self, x = None, y = None):
        self.posx = x
        self.posy = y

    def get_posx(self):
        return self.posx

    def get_posy(self):
        return self.posy

    def set_posx(self, posx):
        self.posx = posx

    def set_posy(self, posy):
        self.posy = posy

    def __str__(self):
        return f"{self.posx},{self.posy}"

class Cell:
    def __init__(self, completed = None, empty = None):
        self.completed = completed
        self.empty = empty
    
    def get_completed(self):
        return self.completed

    def set_completed(self, completed):
        self.completed = completed
    
    def __str__(self):
        return str(self.completed)

    def is_empty(self):
        return self.empty

class InputRune(Rune,Predicate):
    predicate_name = 'inputRune'

    def __init__(self, rune_type = None, color = None):
        Rune.__init__(self,rune_type,color)
        Predicate.__init__(self, [("rune_type"),("color")])

    def __str__(self):
        return f"{self.predicate_name}({Rune.__str__(self)})"


class BusyCell(Position,Rune,Cell,Predicate):
    predicate_name = 'busyCell'

    def __init__(self, posx = None, posy = None, rune_type = None, color = None, completed = None):
        Predicate.__init__(self, [("posx"),("posy"),("rune_type"),("color"),("completed")])
        Position.__init__(self,posx,posy)
        Rune.__init__(self,rune_type,color)
        Cell.__init__(self,completed,False)

    def __str__(self):
        return f"{self.predicate_name}({Position.__str__(self)},{Rune.__str__(self)},{Cell.__str__(self)})"


class EmptyCell(Position, Cell, Predicate):
    predicate_name = 'emptyCell'

    def __init__(self, posx = None, posy = None, completed = None):
        Predicate.__init__(self, [("posx"),("posy"),("completed")])
        Position.__init__(self,posx,posy)
        Cell.__init__(self,completed,True)

    def __str__(self):
        return f"{self.predicate_name}({Position.__str__(self)}, {Cell.__str__(self)})."


class SizeOfMatrix(Predicate):
    predicate_name = 'sizeOfMatrix'

    def __init__(self, size = None):
        Predicate.__init__(self, [("size")])
        self.size = size

    def get_size(self):
        return self.size

    def set_size(self, size):
        self.size = size

    def __str__(self):
        #return "%s(%d).".format(self.predicate_name,self.size)
        return f"{self.predicate_name}({self.size})."


class Solution(Position,Predicate):
    predicate_name = 'solution'

    def __init__(self, posx = None, posy = None):
        Predicate.__init__(self, [("posx"),("posy")])
        Position.__init__(self,posx,posy)

    def __str__(self):
        return f"{self.predicate_name}({Position.__str__(self)})."

class LifePoints(Predicate):
    predicate_name = "lifePoints"

    def __init__(self,points = None):
        self.points = points
        Predicate.__init__(self,[("points")])

    def get_points(self):
        return self.points

    def set_points(self,points = None):
        self.points = points
