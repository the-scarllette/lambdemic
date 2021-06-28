class Card:

    def __init__(self, name):
        self.name = name
        self.discarded = False

    def get_name(self):
        return self.name

    def discard(self):
        self.discarded = True

    def has_name(self, to_check):
        return to_check == self.name