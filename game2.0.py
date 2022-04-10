from city import City
from deck import Deck
from citycard import CityCard
from player import Player
import json


class Game:
    starting_cities = {'blue': 'Atlanta',
                       'yellow': 'Lagos',
                       'black': 'Moscow',
                       'red': 'Sydney'}

    all_colours = ['blue', 'yellow', 'black', 'red']

    game_data_path = 'game_data.json'

    actions = {}

    infection_rate_track = [2, 2, 2, 3, 3, 4, 4]

    def __init__(self, colours=all_colours,
                 player_count=2, num_epidemics=4):
        self.cubes = None
        self.window = None
        self.colours = colours
        self.player_count = 2

        # Defining state space
        self.num_cites = 0
        with open(Game.game_data_path) as f:
            self.game_data = json.load(f)
            self.num_cites = sum([len(self.game_data[colour]) for colour in self.colours])
        self.city_names = {colour: [] for colour in self.colours}
        for colour in self.colours:
            for city_name in self.game_data[colour]:
                self.city_names[colour].append(city_name)
        num_colours = len(self.colours)
        self.state_shape = (self.num_cites * ((3 * num_colours) + (2 * self.player_count) + 3)) +\
                           (num_colours + player_count + 2)

        # Defining Action space
        self.action_functions = {self.build: {'name': 'build', 'use_colour': False},
                                 self.cure: {'name': 'cure', 'use_colour': True},
                                 self.give: {'name': 'give', 'use_colour': False},
                                 self.take: {'name': 'take', 'use_colour': False},
                                 self.treat: {'name': 'treat', 'use_colour': True}}
        self.actions = []
        for function in self.action_functions:
            to_add = [[function, city_name] for city_name in self.city_names]
            if not self.action_functions[function]['use_colour']:
                for elm in to_add:
                    elm.append(None)
            else:
                new_to_add = [elm + [colour] for elm in to_add for colour in self.colours]
                to_add = new_to_add
            self.actions += to_add
        self.action_space = len(self.actions)

        self.current_turn = 0
        self.cities = None
        self.player_deck = None
        self.infection_deck = None
        self.players = None
        self.num_outbreaks = 0
        self.infection_rate_index = 0
        self.cure_tracker = None
        self.research_stations = None
        self.num_epidemics = 4

        self.game_finished = True
        return

    def add_cubes(self, city, colour, num_cubes):
        total_added = 0
        for _ in num_cubes:
            total_added += city.inc_cubes(colour)
        self.cubes[colour] += total_added
        return

    def add_research_station(self, city):
        if city in self.research_stations:
            return
        city.set_has_res_station(True)
        self.research_stations.append(city)
        return

    def build(self, city):
        return

    def cure(self, city, colour):
        return

    def fill_connected_cities(self, city):
        connected_names = self.game_data[city.get_colour()][city.get_name()]
        connected_cities = []
        for name in connected_names:
            city_to_add = self.get_city_by_name(name)
            if city_to_add.get_colour in self.colours:
                connected_cities.append(city_to_add)
        city.set_connected_cities(connected_cities)
        return

    # Add get actions
    def get_action_space(self):
        return

    # Add get after state
    def get_after_state(self, action):
        after_state = None
        return after_state

    def get_city_by_name(self, name):
        for city in self.cities:
            if city.has_name(name):
                return city
        return None

    # Add get state space
    def get_state_space(self):
        return

    def give(self, city):
        return

    def reset(self):
        # New Cities
        self.cities = []
        for colour in self.colours:
            city_names = self.game_data[colour]
            self.cities += [City(city_name, colour) for city_name in city_names]
        for city in self.cities:
            self.fill_connected_cities(city)

        # New Player and Infection Deck
        self.player_deck, self.infection_deck = Deck()
        for city in self.cities:
            self.infection_deck.add_card(CityCard(city))
            self.player_deck.add_card(CityCard(city))
        self.infection_deck.shuffle()
        self.player_deck.shuffle()

        # Cure tracker
        self.cure_tracker = {colour: False for colour in self.colours}
        # Reset outbreak track
        self.num_outbreaks = 0
        # Reset infection track
        self.infection_rate_index = 0

        # Reset Research stations
        self.research_stations = []

        # New player locations and research station
        for colour in Game.starting_cities:
            if colour in self.colours:
                start_city_name = Game.starting_cities[colour]
                break
        start_city = self.get_city_by_name(start_city_name)
        self.add_research_station(start_city)

        # New Players
        self.players = [Player(str(i), start_city) for i in range(self.player_count)]

        # New Player hands
        cards_per_player = (6 - self.__player_count)
        for player in self.players:
            for _ in range(cards_per_player):
                card_to_draw = self.player_deck.draw_card()
                player.add_to_hand(card_to_draw)

        # New Current turn
        self.current_turn = 0

        # New epidemics
        self.player_deck.add_epidemics(self.num_epidemics)

        # Infect new cities
        self.cubes = {colour: 0 for colour in self.colours}
        for cubes_to_place in range(1, 4):
            for _ in range(3):
                city = self.get_city_by_name(self.__infection_deck.draw_and_discard().get_name())
                self.add_cubes(city, city.get_colour(), cubes_to_place)

        self.game_finished = False
        state = None
        return state

    # Add step
    def step(self, action):
        if self.game_finished:
            print("Must call reset before invoking step")
        next_state, reward, terminal, info = None
        return next_state, reward, terminal, info

    def take(self, city):
        return

    def treat(self, city, colour):
        return
