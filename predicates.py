from languages.predicate import Predicate

class InputRune(Predicate):
    predicate_name = 'inputRune'

    def __init__(self, typeOfRune = None, color = None):
        Predicate.__init__(self, [("typeOfRune"),("color")])
        self.typeOfRune = typeOfRune
        self.color = color

    def get_typeOfRune(self):
        return self.typeOfRune

    def get_color(self):
        return self.color

    def set_typeOfRune(self, typeOfRune):
        self.typeOfRune = typeOfRune

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return "inputRune(" + str(self.typeOfRune) + "," + str(self.color) + ")."


class BusyCell(Predicate):
    predicate_name = 'busyCell'

    def __init__(self, posx = None, posy = None, typeOfRune = None, color = None, completed = None):
        Predicate.__init__(self, [("posx"),("posy"),("typeOfRune"),("color"),("completed")])
        self.posx = posx
        self.posy = posy
        self.typeOfRune = typeOfRune
        self.color = color
        self.completed = completed

    def get_posx(self):
        return self.posx

    def get_posy(self):
        return self.posx

    def get_typeOfRune(self):
        return self.typeOfRune

    def get_color(self):
        return self.color

    def get_completed(self):
        return self.completed

    def set_posx(self, posx):
        self.posx = posx

    def set_posy(self, posy):
        self.posy = posy

    def set_typeOfRune(self, typeOfRune):
        self.typeOfRune = typeOfRune

    def set_color(self, color):
        self.color = color

    def set_completed(self, completed):
        self.completed = str(completed).lower()

    def is_empty(self):
        return False

    def __str__(self):
        return "busyCell(" + str(self.posx) + "," + str(self.posy) + "," + str(self.typeOfRune) + "," + str(self.color) + "," + str(self.completed) + ")."


class EmptyCell(Predicate):
    predicate_name = 'emptyCell'

    def __init__(self, posx = None, posy = None, completed = None):
        Predicate.__init__(self, [("posx"),("posy"),("completed")])
        self.posx = posx
        self.posy = posy
        self.completed = completed

    def get_posx(self):
        return self.posx

    def get_posy(self):
        return self.posy

    def get_completed(self):
        return self.completed

    def set_posx(self, posx):
        self.posx = posx

    def set_posy(self, posy):
        self.posy = posy

    def set_completed(self, completed):
        self.completed = completed

    def is_empty(self):
        return True

    def __str__(self):
        return "emptyCell(" + str(self.posx) + "," + str(self.posy) + "," + str(self.completed) + ")."


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
        return "sizeOfMatrix(" + str(self.size) + ")."


class Solution(Predicate):
    predicate_name = 'solution'

    def __init__(self, posx = None, posy = None):
        Predicate.__init__(self, [("posx"),("posy")])
        self.posx = posx
        self.posy = posy

    def get_posx(self):
        return self.posx

    def get_posy(self):
        return self.posx

    def set_posx(self, posx):
        self.posx = posx

    def set_posy(self, posy):
        self.posy = posy

    def __str__(self):
        return "solution(" + str(self.posx) + "," + str(self.posy) + ")."
