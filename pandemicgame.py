from citycard import City, CityCard
from deck import Deck

import json
import numpy as np

# TODO: Add roles
# TODO: Change actions to primitive ones
# TODO: Change step function to account for card holding


class PandemicGame:
    starting_cities = {'blue': 'Atlanta',
                       'yellow': 'Lagos',
                       'black': 'Moscow',
                       'red': 'Sydney'}

    all_colours = ['blue', 'yellow', 'black', 'red']

    game_data_path = 'game_data.json'

    infection_rate_track = [2, 2, 2, 3, 3, 4, 4]

    max_action_points = 4
    max_cubes = 25
    max_outbreaks = 8

    def __init__(self, colours=all_colours,
                 player_count=2, num_epidemics=4):

        self.action_points_left = 0
        self.cubes = None
        self.colours = colours
        self.cured = {colour: False for colour in self.colours}
        self.current_player = None
        self.current_turn = 0
        self.discard_card_phase = False
        self.epidemics_drawn = 0
        self.infection_deck = None
        self.infection_rate_tracker = 0
        self.num_colours = len(self.colours)
        self.num_epidemics = num_epidemics
        self.num_outbreaks = 0
        self.player_count = player_count
        self.player_deck = None
        self.research_stations = None
        self.terminal = True

        # Creating Game board
        with open(PandemicGame.game_data_path) as f:
            self.game_data = json.load(f)
            self.num_cites = sum([len(self.game_data[colour]) for colour in self.colours])
        self.city_names = {colour: [city_name for city_name in self.game_data[colour]]
                           for colour in self.colours}
        # Cities
        self.cities = {city_name: City(city_name, colour) for colour in self.colours
                       for city_name in self.game_data[colour]}
        for colour in self.colours:
            for city_name in self.city_names[colour]:
                connected_cities = []
                for name in self.game_data[colour][city_name]:
                    try:
                        to_connect = self.cities[name]
                        connected_cities.append(to_connect)
                    except KeyError:
                        continue
                self.cities[city_name].set_connenected_cities(connected_cities)
        # Getting start city name
        for colour in PandemicGame.starting_cities:
            if colour in self.colours:
                self.start_city = self.cities[PandemicGame.starting_cities[colour]]
                break

        # Players
        self.players = [PandemicPlayer(str(i), self.start_city)
                        for i in range(self.player_count)]

        # Defining Actions
        # DRIVE/FERRY:
        #   For each city:
        #       Move to that city
        # DIRECT FLIGHT:
        #   For each city card:
        #       discard that card and move to the city
        # CHARTER FLIGHT:
        #   For every other city:
        #         Discard the current city card and move to the other city
        # SHUTTLE FLIGHT:
        #   For each city:
        #       Move to that city
        # BUILD
        #   Discard the current city card and build a research station
        # GIVE CARD/Take Card
        #   For every other players
        #       Trade the current city card between the current and other player
        # TREAT DISEASE
        #   For each colour:
        #       Treat disease
        # CURE
        #   For each colour:
        #       Cure disease
        # For each card:
        #   Discard that card
        self.num_actions = (5 * self.num_cites) + self.player_count + (2 * self.num_colours) + 1
        self.possible_actions = list(range(self.num_actions))

        def make_dict(action, parameter):
            return {'action': action, 'parameter': parameter}
        self.action_key = [make_dict(action, self.cities[city_name])
                           for city_name in self.cities
                           for action in
                           [self.move_player, self.direct_flight, self.charter_flight,
                            self.shuttle_flight, self.discard_card]] +\
                          [make_dict(action, colour) for colour in self.colours
                           for action in [self.treat_disease, self.cure]] +\
                          [make_dict(self.trade_card, player) for player in self.players] +\
                          [make_dict(self.build, None)]

        # NUM_CITIES = C, NUM_COLOURS = D, PLAYER_COUNT = P
        # C(3D + 2P + 1 + 1 + 1) + D + P + 2
        # EACH CITY:
        #   ECH COLOUR: 1 CUBE, 2 CUBE, 3 CUBE
        #   EACH PLAYER: IN CITY, CARD IN HAND
        #   Has research station
        #   City card in discard pile
        #   Infection card in discard pile
        # Each colour: Is cured
        # Each player: current turn
        self.state_shape = (self.num_cites * ((3 * self.num_colours) + (2 * self.player_count) + 3) +
                            self.num_colours + self.player_count + PandemicGame.max_action_points + 2)

        return

    def add_cubes(self, city, colour, num_cubes):
        total_added = 0
        outbreaks = 0
        for _ in range(num_cubes):
            cubes_to_add, outbreaks_to_add = city.inc_cubes(colour)
            total_added += cubes_to_add
            outbreaks += outbreaks_to_add
        self.cubes[colour] += total_added
        self.num_outbreaks += outbreaks_to_add

        self.num_outbreaks = min(self.num_outbreaks, PandemicGame.max_outbreaks)
        self.cubes[colour] = min(self.cubes[colour], PandemicGame.max_cubes)
        return

    def build(self, param=None):
        return

    def charter_flight(self, city):
        return

    def cure(self, colour):
        return

    def direct_flight(self, city):
        return

    def discard_card(self, city):
        return

    def get_current_possible_actions(self):
        current_possible_actions = []
        for i in range(self.possible_actions):
            action_param = self.possible_actions[i]
            if self.is_action_possible(action_param['action'], action_param['parameter']):
                current_possible_actions.append(i)
        return current_possible_actions

    def get_current_state(self):
        current_state = []

        for city_name in self.cities:
            city = self.cities[city_name]
            city_state_array = [city.get_cubes(colour) == cube_num
                                for colour in self.colours for cube_num in range(1, 4)]
            city_state_array += ([player.in_city(city), player.is_city_in_hand(city)] for player in self.players)
            city_state_array += [city.has_research_station(),
                                 self.player_deck.city_in_discard_pile(city),
                                 self.infection_deck.city_in_discard_pile(city)]
            current_state += city_state_array.copy()

        current_state += [self.cured[colour] for colour in self.colours]
        player_turn_array = [False] * self.player_count
        player_turn_array[self.current_turn] = True
        current_state += player_turn_array

        current_state += [self.discard_card_phase]

        action_points_array = [False] * (PandemicGame.max_action_points + 1)
        action_points_array[self.action_points_left] = True
        current_state += action_points_array

        current_state = np.array(current_state, dtype=np.bool_)
        return current_state

    def is_action_possible(self, action, param):

        if self.discard_card_phase:
            return action == self.discard_card and self.current_player.is_city_in_hand(param)

        if self.action_points_left <= 0:
            return False

        if action == self.move_player:
            return any(self.current_player.in_city(city) for city in param.get_connected_cities())
        elif action == self.direct_flight:
            return self.current_player.is_city_in_hand(param)
        elif action == self.charter_flight or action == self.build:
            return self.current_player.is_current_city_in_hand()
        elif action == self.shuttle_flight:
            return (self.current_player.get_city().has_research_station() and
                    param.has_research_station())
        elif action == self.trade_card:
            return self.current_player.get_city().equals(param.get_city()) and\
                   (self.current_player.is_current_city_in_hand() or param.is_current_city_in_hand())
        elif action == self.treat_disease:
            return self.current_player.get_city().get_cubes(param) > 0
        elif action == self.cure:
            return self.current_player.get_city().has_research_station and\
                   (self.current_player.can_cure(param))

        return False

    def move_player(self, target_city):
        return None

    def reset(self):
        # Resetting Cities
        for city in self.cities:
            city.reset()

        # New Player and Infection Deck
        self.player_deck = Deck()
        self.infection_deck = Deck()
        for deck in [self.player_deck, self.infection_deck]:
            deck.add_cards(CityCard(city) for city in self.cities)
            deck.shuffle()

        # Cure Tracker
        self.cured = {colour: False for colour in self.colours}

        # Outbreak Track
        self.num_outbreaks = 0

        # Infection Track
        self.infection_rate_tracker = 0

        # Research Stations
        self.research_stations = [self.start_city]
        self.start_city.set_has_research_station(True)

        # New Player hands
        for player in self.players:
            player.reset(self.start_city)
        cards_per_player = range((6 - self.player_count))
        for player in self.players:
            player.add_multiple_to_hand(self.player_deck.draw_card()
                                        for _ in cards_per_player)

        # New Current Turn
        self.current_turn = 0
        self.current_player = self.players[0]

        # New Epidemics
        self.player_deck.add_epidemics(self.num_epidemics)
        self.epidemics_drawn = 0

        # Infect Cities
        self.cubes = {colour: 0 for colour in self.colours}
        for cubes_to_place in range(1, 4):
            city_to_infect = self.infection_deck.draw_and_discard().get_city()
            self.add_cubes(city_to_infect, city_to_infect.get_colour(), cubes_to_place)

        # Game not terminal
        self.discard_card_phase = False
        self.terminal = False

        return

    def step(self, action):
        current_possible_actions = self.get_current_possible_actions()
        if action not in current_possible_actions:
            raise AttributeError(str(action) + " is and invalid action for current state")

        # Get action and param
        # Do action with param

        # In turn action
        #   decrement action points
        #   Check for all cured
        #   if end of turn
        #       Draw cards: check for loss
        #       Infect cities: check for loss
        #       if discard needed:
        #           set to discard phase
        #       Else:
        #           move to next player and reset action points
        # Else:
        #   if under hand limit
        #       Move to next player and reset action points
        #   Else:
        #       Stay in discard phase
        return

    def shuttle_flight(self, city):
        return

    def trade_card(self, player):
        return

    def treat_disease(self, colour):
        return


class PandemicPlayer:

    cards_needed_to_cure = 5

    def __init__(self, name, city):
        self.__city = city
        self.__name = name
        self.__hand = []
        self.__cards_in_hand = 0
        return

    def add_to_hand(self, card):
        self.__hand.append(card)
        self.__cards_in_hand += 1
        return

    def add_multiple_to_hand(self, *cards):
        for card in cards:
            self.add_to_hand(card)
        return

    def can_cure(self, colour):
        cards_needed = PandemicPlayer.cards_needed_to_cure
        for card in self.__hand:
            if card.has_colour(colour):
                cards_needed -= 1
                if cards_needed <= 0:
                    return True
        return False

    def discard_card_by_name(self, card_name):
        for i in range(self.__cards_in_hand):
            discarded = self.__hand[i]
            if discarded.has_name(card_name):
                del self.__hand[i]
                self.__cards_in_hand -= 1
                return discarded
        return None

    def equals(self, other_player):
        return self.has_name(other_player.get_name())

    def get_city(self):
        return self.__city

    def get_city_name(self):
        return self.__city.get_name()

    def get_connected_cities(self):
        return self.__city.get_connected_cities()

    def get_hand(self):
        return self.__hand

    def get_hand_size(self):
        return self.__cards_in_hand

    def get_name(self):
        return self.__name

    def set_city(self, city):
        self.__city = city

    def has_card(self, card_to_check):
        for card in self.__hand:
            if card.equals(card_to_check):
                return True
        return False

    def has_name(self, name):
        return self.__name == name

    def in_city(self, city):
        return self.__city.equals(city)

    def is_current_city_in_hand(self):
        return self.discard_card_by_name(self.__city)

    def is_city_in_hand(self, city_to_check):
        for card in self.__hand:
            if card.get_name() == city_to_check.get_name():
                return True
        return False

    def reset(self, city):
        self.__city = city
        self.__hand = []
        self.__cards_in_hand = 0
        return
