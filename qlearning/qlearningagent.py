from player import Player

class QLearningAgent(Player):

    def __init__(self):
        super().__init__()
        return

    def discard_card_by_name(self, card_name):
        return False

    def is_city_in_hand(self):
        return False