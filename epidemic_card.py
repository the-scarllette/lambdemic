from card import Card

class EpidemicCard(Card):

    def __init__(self):
        super().__init__("epidemic")
        self.is_epidemic = True