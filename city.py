from gameobject import GameObject

class City(GameObject):

    def __init__(self, name, colour, connected_cities=[], window=None, x=-1, y=-1, game=None):
        super().__init__(window, x, y)
        self.__name = name
        self.__colour = colour
        self.__connected_cities = connected_cities.copy()
        self.__game = game
        self.__radius = 10
        self.__left_city = False
        self.__right_city = False
        self.__cubes = {"blue": 0, "yellow": 0, "black": 0, "red": 0}
        self.__has_outbreaked = False

    def get_center(self):
        return self.__center

    def get_colour(self):
        return self.__colour

    def get_connected_cities(self):
        return self.__connected_cities.copy()

    def get_cubes(self, colour):
        return self.__cubes[colour]

    def get_name(self):
        return self.__name

    def has_name(self, name):
        return self.__name == name

    def set_connected_cities(self, to_set):
        self.__connected_cities = to_set.copy()
        return

    def set_cubes(self, colour, to_set):
        self.__cubes[colour] = to_set
        return

    def set_left_city(self, to_set):
        self.__left_city = to_set
        return

    def set_right_city(self, to_set):
        self.__right_city = to_set
        return

    def set_has_outbreaked(self, to_set):
        self.__has_outbreaked = to_set
        return

    def set_has_res_station(self, to_set):
        self.__has_res_station = to_set
        if to_set and self.__game is not None:
            self.__game.add_res_station(self)
        return

    def click(self):
        self.inc_cubes(self.__colour)

    def draw_city(self):
        if self.window is None:
            return
        self.__image.undraw()
        self.__image.draw(self.window)
        self.__name_text.undraw()
        self.__name_text.draw(self.window)
        self.__res_station_image.undraw()
        if self.__has_res_station:
            self.__res_station_image.draw(self.window)

    def draw_cubes(self):
        if self.window is None:
            return
        for cube_text in self.__cube_text.values():
            cube_text.undraw()
            cube_text.draw(self.window)

    def equals(self, to_check):
        return self.__name == to_check.get_name()

    def has_research_station(self):
        return self.__has_res_station

    def dec_cubes(self, colour):
        if self.__cubes[colour] > 0:
            self.__cubes[colour] -= 1
            self.__cube_text[colour].setText(str(self.__cubes[colour]))
            self.draw_cubes()
        return

    def inc_cubes(self, colour):
        total_added = 0
        outbreaks = 0
        if self.__cubes[colour] >= 3:
            outbreaks += 1
            if not self.__has_outbreaked:
                self.__has_outbreaked = True
                for city in self.__connected_cities:
                    cubes_added, outbreaks_added = city.inc_cubes(colour)
                    total_added += cubes_added
                    outbreaks += outbreaks_added
        else:
            self.__cubes[colour] += 1
            total_added += 1
        return total_added, outbreaks

    def is_clicked(self, mouse_x, mouse_y):
        return ((self.x - mouse_x)**2 + (self.y - mouse_y)**2) <= self.__radius**2

    def is_left_city(self):
        return self.__left_city

    def is_right_city(self):
        return self.__right_city
