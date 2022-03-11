from card import Card
from city import City

class CityCard(Card):

    def __init__(self, city):
        self.__city = city
        super().__init__(self.__city.get_name())
        self.is_epidemic = False

    def get_city(self):
        return self.__city

    def get_colour(self):
        return self.__city.get_colour()
    
    def has_city(self, city):
        return city.has_name(self.get_name())

    def has_colour(self, colour):
        return self.get_colour() == colour
