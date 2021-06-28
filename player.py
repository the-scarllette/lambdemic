from gameobject import GameObject
from city import City
from graphics import *

class Player(GameObject):

    def __init__(self, name, window, city, colour, draw_offset):
        self.__city = city
        self.__name = name
        self.__draw_offset = draw_offset
        super().__init__(window, self.__city.get_x(), self.__city.get_y())
        self.__pawn = Circle(Point(self.x + 15 + self.__draw_offset, self.y), 5)
        self.__pawn.setFill(colour)

        self.__text = Text(Point(50 + 20*self.__draw_offset, 400), self.__name)
        self.__click_box = Rectangle(Point(20 + 20*self.__draw_offset, 390), Point(80 + 20*self.__draw_offset, 410))
        self.__click_box.setFill(colour)

        self.__hand = []
        self.__hand_image = []

        self.__cards_in_hand = 0

    def get_name(self):
        return self.__name

    def set_city(self, city):
        self.__city = city

    def add_to_hand(self, card):
        self.__hand.append(card)
        text = Text(Point(50 + 20 * self.__draw_offset, 420 + self.__cards_in_hand*15), card.get_name())
        text.setFill(card.get_colour())
        self.__hand_image.append(text)
        self.__cards_in_hand += 1

    def click(self):
        print("Enter the card to add to the hand of " + self.__name)
        to_add = input()
        print(to_add)

    def discard_card_by_name(self, card_name):
        discarded = False
        i = 0
        while i < self.__cards_in_hand:
            if discarded:
                self.__hand_image[i].move(0, -15)
            if self.__hand[i].has_name(card_name):
                self.__hand[i].discard()
                self.__hand_image[i].undraw()
                del self.__hand[i]
                del self.__hand_image[i]
                self.__cards_in_hand -= 1
                discarded = True
            else:
                i += 1

        return discarded

    def draw(self):
        self.__pawn.undraw()
        self.__pawn.draw(self.window)

        self.__click_box.undraw()
        self.__click_box.draw(self.window)
        self.__text.undraw()
        self.__text.draw(self.window)

        for i in range(self.__cards_in_hand):
            self.__hand_image[i].undraw()
            self.__hand_image[i].draw(self.window)

    def has_name(self, name):
        return self.__name == name

    def is_clicked(self, mouse_x, mouse_y):
        start_x = 20 + 20*self.__draw_offset
        start_y = 390
        return (start_x <= mouse_x) and (mouse_x <= start_x + 60) and (start_y <= mouse_y) and (mouse_y <= start_y + 20)