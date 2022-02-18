from city import City

'''Possible actions
move
charter
direct
shuttle'''

class PathNode:

    def __init__(self, city, cost, prev_node=None, action=None, used_card=None):
        self.__city = city
        self.__cost = cost
        self.__action_to_arrive = action
        self.__previous_node = prev_node
        self.__used_card = used_card
        self.__next_node = None
        self.__action_to_get_to_next = None
        return

    def get_arriving_action(self):
        return self.__action_to_arrive

    def get_city(self):
        return self.__city

    def get_connected_cities(self):
        return self.__city.get_connected_cities()

    def get_cost(self):
        return self.__cost

    def get_name(self):
        return self.__city.get_name()

    def get_next_action(self):
        return self.__action_to_get_to_next

    def get_next_node(self):
        return self.__next_node

    def get_previous_node(self):
        return self.__previous_node

    def get_total_cost(self):
        current_node = self

        while current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()

        return current_node.get_cost()

    def get_used_card(self):
        return self.__used_card

    def has_research_station(self):
        return self.__city.has_research_station()

    def set_action_to_get_to_next(self, action):
        self.__action_to_get_to_next = action

    def set_next_node(self, to_set):
        self.__next_node = to_set

    def set_previous_city(self, city, action):
        self.__previous_city = city
        self.__action_to_arrive = action
