from graphics import *
from gameobject import GameObject

class OutbreakTracker(GameObject):

    def __init__(self, window):
        super().__init__(window, 900, 100)
        self.__outbreaks = 0
        self.__image = Polygon(Point(self.x - 20, self.y), Point(self.x, self.y - 20), Point(self.x + 20, self.y), Point(self.x, self.y + 20))
        self.__image.setFill("red")
        self.__text = Text(Point(self.x, self.y), "0")

    def get_outbreaks(self):
        return self.__outbreaks

    def draw(self):
        if self.window is None:
            return
        self.__image.draw(self.window)
        self.__text.draw(self.window)

    def inc_outbreaks(self):
        self.__outbreaks += 1
        self.__text.setText(str(self.__outbreaks))