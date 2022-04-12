class GameObject:

    def __init__(self, window, x, y):
        self.window = window
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y
        return

    def click(self):
        return

    def draw(self):
        if self.window is None:
            return
        return
