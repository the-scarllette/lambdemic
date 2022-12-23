
class City:

    def __init__(self, name, colour, connected_cities=[]):
        self.__name = name
        self.__colour = colour
        self.__connected_cities = connected_cities.copy()
        self.__cubes = {"blue": 0, "yellow": 0, "black": 0, "red": 0}
        self.__has_outbreaked = False
        self.__has_res_station = False
        return

    def dec_cubes(self, colour):
        if self.__cubes[colour] > 0:
            self.__cubes[colour] -= 1
        return

    def get_colour(self):
        return self.__colour

    def get_connected_cities(self):
        return self.__connected_cities.copy()

    def get_cubes(self, colour=None):
        if colour is not None:
            return self.__cubes[colour]
        return self.__cubes

    def get_name(self):
        return self.__name

    def equals(self, city):
        return self.__name == city.get_name()

    def has_name(self, name):
        return self.__name == name

    def has_research_station(self):
        return self.__has_res_station

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

    def set_connected_cities(self, to_set):
        self.__connected_cities = to_set.copy()
        return

    def set_cubes(self, colour, to_set):
        self.__cubes[colour] = to_set
        return

    def set_has_outbreaked(self, to_set):
        self.__has_outbreaked = to_set
        return

    def set_has_res_station(self, to_set):
        self.__has_res_station = to_set
        return

    def reset(self):
        self.__cubes = {"blue": 0, "yellow": 0, "black": 0, "red": 0}
        self.__has_outbreaked = False
        self.__has_res_station = False
        return
