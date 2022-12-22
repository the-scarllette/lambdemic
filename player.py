

class Player:

    cards_needed_to_cure = 5

    def __init__(self, name, city):
        self.__city = city
        self.__name = name
        self.__hand = []
        self.__cards_in_hand = 0
        return

    def add_to_hand(self, card):
        self.__hand.append(card)
        self.__cards_in_hand += 1
        return

    def add_multiple_to_hand(self, *cards):
        for card in cards:
            self.add_to_hand(card)
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

    def set_city(self, city):
        self.__city = city
    
    def can_cure(self, colour):
        cards_needed = Player.cards_needed_to_cure
        for card in self.__hand:
            if card.has_colour(colour):
                cards_needed -= 1
                if cards_needed <= 0:
                    return True
        return False

    def discard_card_by_name(self, card_name):
        for i in range(self.__cards_in_hand):
            discarded = self.__hand[i]
            if discarded.has_name(card_name):
                del self.__hand[i]
                self.__cards_in_hand -= 1
                return discarded
        return None

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

    def reset(self, city):
        self.__city = city
        self.__hand = []
        self.__cards_in_hand = 0
        return
