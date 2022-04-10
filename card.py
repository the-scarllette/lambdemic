class Card:

    def __init__(self, name):
        self.name = name
        self.discarded = False
        self.is_epidemic = False
        return

    def get_name(self):
        return self.name

    def discard(self):
        self.discarded = True

    def equals(self, to_check):
        if to_check is None:
            return False
        return self.has_name(to_check.get_name())

    def has_name(self, to_check):
        return to_check == self.name

    def is_epidemic(self):
        return self.is_epidemic
