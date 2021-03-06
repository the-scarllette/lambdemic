from gameobject import GameObject
from city import City


class Player(GameObject):

    def __init__(self, name, draw=False, window=None, city=None, colour=None, draw_offset=None):
        self.__colour = colour
        self.__city = city
        self.__name = name
        self.__draw_offset = draw_offset
        self.__draw = draw
        if self.__draw:
            super().__init__(window, self.__city.get_x(), self.__city.get_y())
            self.__pawn = Circle(Point(self.x + 15 + self.__draw_offset, self.y), 5)
            self.__pawn.setFill(self.__colour)

            self.__text = Text(Point(50 + 20*self.__draw_offset, 400), self.__name)
            self.__click_box = Rectangle(Point(20 + 20*self.__draw_offset, 390), Point(80 + 20*self.__draw_offset, 410))
            self.__click_box.setFill(colour)

            self.__hand_image = []
        self.__hand = []
        self.__cards_in_hand = 0
        return

    def act(self):
        return

    def get_city(self):
        return self.__city

    def get_city_name(self):
        return self.__city.get_name()

    def get_connected_cities(self):
        return self.__city.get_connected_cities()

    def get_hand(self):
        return self.__hand

    def get_hand_size(self):
        return self.__cards_in_hand

    def get_name(self):
        return self.__name

    def get_results_filename(self):
        return

    def set_city(self, city):
        self.__city = city

    def add_to_hand(self, card):
        self.__hand.append(card)
        if self.__draw:
            text = Text(Point(50 + 20 * self.__draw_offset, 420 + self.__cards_in_hand*15), card.get_name())
            text.setFill(card.get_colour())
            self.__hand_image.append(text)
        self.__cards_in_hand += 1
        return
    
    def can_cure(self, colour):
        cards_needed = 5
        for card in self.__hand:
            if card.has_colour(colour):
                cards_needed -= 1
                if cards_needed <= 0:
                    return True
        return False

    def click(self):
        print("Enter the card to add to the hand of " + self.__name)
        to_add = input()
        print(to_add)
        return

    def discard_card_by_name(self, card_name):
        for i in range(self.__cards_in_hand):
            discarded = self.__hand[i]
            if discarded.has_name(card_name):
                del self.__hand[i]
                self.__cards_in_hand -= 1
                return discarded
        return None

    def draw(self):
        if not self.__draw:
            return
        self.__pawn.undraw()
        self.__pawn = Circle(Point(self.x + 15 + self.__draw_offset, self.y), 5)
        self.__pawn.setFill(self.__colour)
        self.__pawn.draw(self.window)

        self.__click_box.undraw()
        self.__click_box.draw(self.window)
        self.__text.undraw()
        self.__text.draw(self.window)

        for i in range(self.__cards_in_hand):
            self.__hand_image[i].undraw()
            self.__hand_image[i].draw(self.window)
        return

    def equals(self, other_player):
        return self.has_name(other_player.get_name())

    def has_card(self, card_to_check):
        for card in self.__hand:
            if card.equals(card_to_check):
                return True
        return False

    def has_name(self, name):
        return self.__name == name
    
    def in_city(self, city):
        return self.__city.equals(city)

    def is_current_city_in_hand(self):
        return self.discard_card_by_name(self.__city)

    def is_city_in_hand(self, city_to_check):
        for card in self.__hand:
            if card.get_name() == city_to_check.get_name():
                return True
        return False

    def is_clicked(self, mouse_x, mouse_y):
        start_x = 20 + 20*self.__draw_offset
        start_y = 390
        return (start_x <= mouse_x) and (mouse_x <= start_x + 60) and (start_y <= mouse_y) and (mouse_y <= start_y + 20)

    def learn(self):
        return

    def move_to(self, new_city):
        self.__city = new_city
        self.x = self.__city.get_x()
        self.y = self.__city.get_y()
        self.draw()
        return

    def observe_reward(self):
        return 0

    def remove_card_by_name(self, card_name):
        removed = False
        i = 0
        while i < self.__cards_in_hand:
            if removed:
                self.__hand_image[i].move(0, -15)
            if self.__hand[i].has_name(card_name):
                self.__hand_image[i].undraw()
                del self.__hand[i]
                del self.__hand_image[i]
                self.__cards_in_hand -= 1
                removed = True
            else:
                i += 1

        return removed

    def reset_hand(self):
        self.__hand = []
        self.__cards_in_hand = 0
        self.draw()
        return
