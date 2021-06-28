from card import Card
from city import City

class CityCard(Card):

    def __init__(self, city):
        self.__city = city
        super().__init__(self.__city.get_name())

    def get_colour(self):
        return self.__city.get_colour()