from gameobject import GameObject
from graphics import *

class CureTracker(GameObject):

    def __init__(self, window, colour, x, y):
        super().__init__(window, x, y)
        self.__colour = colour
        self.__image = Circle(Point(self.x, self.y), 10)
        self.__image.setFill(self.__colour)
        self.__cured = False

    def draw(self):
        if self.window is None:
            return
        self.__image.undraw()
        if self.__cured:
            self.__image.draw(self.window)

    def get_colour(self):
        return self.__colour

    def is_cured(self):
        return self.__cured

    def set_cured(self, to_set):
        self.__cured = to_set