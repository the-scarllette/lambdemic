from random import shuffle, randint
from gameobject import GameObject
from citycard import CityCard
from city import City
from epidemic_card import EpidemicCard


class Deck(GameObject):

    def __init__(self, window=None, x=-1, y=-1):
        super().__init__(window, x, y)
        self.__deck = []
        self.__discard_pile = []
        self.__cards_in_deck = 0
        return

    def add_card(self, to_add):
        self.__deck.append(to_add)
        self.__cards_in_deck += 1
        return

    def add_epidemics(self, epidemics):
        d = self.__cards_in_deck // epidemics
        for i in range(epidemics):
            if i == epidemics - 1:
                index = randint(d*i, self.__cards_in_deck)
            else:
                index = randint(0, d) + d*i
            self.__deck.insert(index, EpidemicCard())
            self.__cards_in_deck += 1
        return

    def city_in_discard_pile(self, city_to_check):
        for card in self.__discard_pile:
            if card.has_name(city_to_check.get_name()):
                return True
        return False

    def discard_card(self, card):
        self.__discard_pile.append(card)
        return

    def draw_and_discard(self):
        card = self.draw_card()
        self.discard_card(card)
        return card

    def draw_bottom_card(self):
        self.__cards_in_deck -= 1
        return self.__deck.pop(0)

    def draw_card(self):
        if self.__cards_in_deck <= 0:
            return None
        self.__cards_in_deck -= 1
        card = self.__deck.pop(self.__cards_in_deck)
        return card

    def get_card_by_name(self, name):
        for i in range(self.__cards_in_deck):
            card = self.__deck[i]
            if card.has_name(name):
                self.__cards_in_deck -= 1
                return self.__deck.pop(i)
        return None
    
    def get_discard_pile(self):
        return self.__discard_pile

    def get_number_of_cards(self):
        return self.__cards_in_deck

    def restack_discard_pile(self):
        shuffle(self.__discard_pile)
        for card in self.__discard_pile:
            self.add_card(card)
        self.__discard_pile = []
        return

    def shuffle(self):
        shuffle(self.__deck)
        return
