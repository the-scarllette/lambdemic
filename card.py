class Card:

    def __init__(self, name):
        self.name = name
        self.discarded = False
        self.is_epidemic = False

    def get_name(self):
        return self.name

    def discard(self):
        self.discarded = True

    def has_name(self, to_check):
        return to_check == self.name

    def is_epidemic(self):
        return self.is_epidemic