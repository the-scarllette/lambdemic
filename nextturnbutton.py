from graphics import *
from gameobject import GameObject

class NextTurnButton(GameObject):

    def __init__(self, window, x, y):
        super().__init__(window, x, y)
        self.__width = 70
        self.__height = 20
        self.__text = Text(Point(self.x + (self.__width / 2), self.y + (self.__height / 2)), "Next turn")
        self.__box = Rectangle(Point(self.x, self.y), Point(self.x + self.__width, self.y + self.__height))
        self.__box.setFill('Red')

    def draw(self):
        if self.window is None:
            return
        self.__box.draw(self.window)
        self.__text.draw(self.window)

    def is_clicked(self, x, y):
        return (self.x <= x <= self.x + self.__width) and (self.y <= y <= self.y + self.__height)