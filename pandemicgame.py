from city import City
from citycard import CityCard
from deck import Deck

import json
from itertools import combinations
import numpy as np

# TODO: Add roles


class PandemicGame:
    starting_cities = {'blue': 'Atlanta',
                       'yellow': 'Lagos',
                       'black': 'Moscow',
                       'red': 'Sydney'}

    all_colours = ['blue', 'yellow', 'black', 'red']

    game_data_path = 'game_data.json'

    infection_rate_track = [2, 2, 2, 3, 3, 4, 4]
    max_infect_rate_tracker = 6

    cards_drawn_each_turn = 2

    max_action_points = 4
    max_cubes = 25
    max_hand_size = 7
    max_outbreaks = 8
    max_research_stations = 6

    cure_reward = 1.0
    failure_reward = -1.0
    step_reward = 0.0
    # step_reward = -0.1
    success_reward = 1.0

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

        def make_dict(action, parameter):
            return {'action': action, 'parameter': parameter}
        self.action_key = [make_dict(action, self.cities[city_name])
                           for city_name in self.cities
                           for action in
                           [self.move_player, self.direct_flight, self.charter_flight,
                            self.shuttle_flight, self.discard_card]] +\
                          [make_dict(self.treat_disease, colour) for colour in self.colours] +\
                          [make_dict(self.trade_card, player) for player in self.players] +\
                          [make_dict(self.build, None)]
        for colour in self.colours:
            colour_cities = [city := self.cities[city_name] for city_name in self.cities if city.get_colour() == colour]
            cure_combinations =  list(combinations(colour_cities, PandemicPlayer.cards_needed_to_cure))
            self.action_key += [make_dict(self.cure, (colour, ) + cure_combination)
                                for cure_combination in cure_combinations]
        self.num_actions = len(self.action_key)
        self.possible_actions = list(range(self.num_actions))


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
                            self.num_colours + self.player_count + PandemicGame.max_action_points + self.num_epidemics + 3)

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
        self.reset_outbreaks()
        return

    def build(self, param=None):
        self.action_points_left -= 1

        self.discard_card(self.current_player.get_city())

        city_to_build_name = self.current_player.get_city().get_name()
        city_to_build = self.cities[city_to_build_name]
        city_to_build.set_has_research_station(True)
        self.research_stations.append(city_to_build)
        return

    def charter_flight(self, city):
        self.action_points_left -= 1

        self.discard_card(self.current_player.get_city())

        self.current_player.set_city(city)
        return

    def cure(self, colour_and_cities):
        self.action_points_left -= 1

        colour = colour_and_cities[0]
        cities = colour_and_cities[1:5]

        for city in cities:
            self.discard_card(city)

        self.cured[colour] = True
        return

    def direct_flight(self, city):
        self.action_points_left -= 1

        self.discard_card(city)

        self.current_player.set_city(city)
        return

    def discard_card(self, city):
        discarded_card = self.current_player.discard_card_by_name(city.get_name())
        self.player_deck.discard_card(discarded_card)
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
        player_turn_array[self.current_turn % self.player_count] = True
        current_state += player_turn_array

        current_state += [self.discard_card_phase]

        action_points_array = [False] * (PandemicGame.max_action_points + 1)
        action_points_array[self.action_points_left] = True
        current_state += action_points_array

        num_epidemics_array = [False] * (self.num_epidemics + 1)
        num_epidemics_array[self.epidemics_drawn] = True
        current_state += num_epidemics_array

        current_state = np.array(current_state, dtype=np.bool_)
        return current_state

    def increment_infection_rate_tracker(self):
        self.infection_rate_tracker = min(self.infection_rate_tracker + 1,
                                          PandemicGame.max_infect_rate_tracker)
        return

    def is_action_possible(self, action, param):

        if self.discard_card_phase:
            return action == self.discard_card and self.current_player.is_city_in_hand(param)

        if self.action_points_left <= 0:
            return False

        if action == self.move_player:
            return any(self.current_player.in_city(city) for city in param.get_connected_cities())
        elif action == self.direct_flight:
            return self.current_player.is_city_in_hand(param)
        elif action == self.charter_flight:
            return self.current_player.is_current_city_in_hand()
        elif action == self.shuttle_flight:
            return (self.current_player.get_city().has_research_station() and
                    param.has_research_station())
        elif action == self.build:
            return self.current_player.is_current_city_in_hand() and\
                   (len(self.research_stations) < PandemicGame.max_research_stations) and\
                   (not self.current_player.get_city().has_research_station())
        elif action == self.trade_card:
            return self.current_player.get_city().equals(param.get_city()) and\
                   (self.current_player.is_current_city_in_hand() or param.is_current_city_in_hand())
        elif action == self.treat_disease:
            return self.current_player.get_city().get_cubes(param) > 0
        elif action == self.cure:
            colour_to_cure = param[0]
            cards_to_use = param[1, 5]
            return (not self.cured[colour_to_cure]) and \
                   self.current_player.get_city().has_research_station and \
                   self.current_player.can_cure(colour_to_cure) and \
                   all(self.current_player.is_city_in_hand(city) for city in cards_to_use)

        return False

    def move_player(self, target_city):
        self.action_points_left -= 1

        self.current_player.set_city(target_city)
        return

    def remove_cubes(self, city, colour, to_remove):
        for _ in range(to_remove):
            city.dec_cubes(colour)

        self.cubes[colour] = max(0, self.cubes[colour] - to_remove)
        return

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

    def reset_outbreaks(self):
        for city_name in self.cities:
            self.cities[city_name].set_has_outbreaked(False)
        return

    def step(self, action):
        current_possible_actions = self.get_current_possible_actions()

        if action not in current_possible_actions:
            raise AttributeError(str(action) + " is and invalid action for current state")

        last_cured = self.cured.copy()
        info = {'cured': [], 'success': False}

        # Get action and param
        action_param = self.action_key[action]
        action = action_param['action']
        parameter = action_param['parameter']

        # Do action with param
        action(parameter)

        # Give rewards
        reward = self.step_reward
        all_cured = True
        for colour in self.colours:
            if self.cured[colour]:
                info['cured'].append(colour)
                if not last_cured[colour]:
                    reward += self.step_reward
            else:
                all_cured = False
        if all_cured:
            reward += self.success_reward
            self.terminal = True
            info['success'] = True
            return self.get_current_state(), reward, True, info

        # In turn action
        #   decrement action points
        #   Check for all cured
        #   if discard needed:
        #         # set to discard phase
        #         # if still need to discard:
        #         # stay in discard phase
        #   if end of turn
        #       Draw cards: check for loss, check for epidemic and check for loss
        #       Infect cities: check for loss
        #       move to next player and reset action points

        def over_hand_limit():
            return self.current_player.get_hand_size() > PandemicGame.max_hand_size

        def is_terminal():
            over_outbreaks = self.num_outbreaks >= self.max_outbreaks
            over_cubes = self.cubes[colour] >= self.max_cubes
            if over_cubes or over_outbreaks:
                failure_reason = {True: 'cubes', False: 'outbreaks'}
                info['failure_reason'] = failure_reason[over_cubes]
                return True
            return False

        # End of player turn
        if not over_hand_limit():
            self.discard_card_phase = False

        if self.action_points_left <= 0 and not self.discard_card_phase:
            # Drawing cards
            for _ in range(PandemicGame.cards_drawn_each_turn):
                card_drawn = self.player_deck.draw_card()
                if card_drawn is None:  # No card, fail game
                    reward += self.failure_reward
                    self.terminal = True
                    info['failure_reason'] = 'out of player cards'
                    return self.get_current_state(), reward, True, info

                elif card_drawn.is_epidemic():  # Epidemic drawn
                    self.player_deck.discard_card(card_drawn)
                    self.epidemics_drawn += 1

                    card_to_infect = self.infection_deck.draw_bottom_card()
                    self.infection_deck.discard(card_to_infect)
                    city_to_infect = card_to_infect.get_city()
                    colour_to_infect = city_to_infect.get_colour()
                    self.add_cubes(city_to_infect, colour_to_infect, 3)

                    self.infection_deck.restack_discard_pile()

                    self.increment_infection_rate_tracker()

                    if is_terminal():
                        reward += self.failure_reward
                        self.terminal = True
                        return self.get_current_state(), reward, True, info

                else:  # Normal card drawn
                    self.current_player.add_to_hand(card_drawn)
                    if over_hand_limit():
                        self.discard_card_phase = True

        if self.action_points_left <= 0 and not self.discard_card_phase:
            # Infect cities
            for _ in range(self.infection_rate_track[self.infection_rate_tracker]):
                card_drawn = self.infection_deck.draw_and_discard()

                if card_drawn is None:
                    self.increment_infection_rate_tracker()
                    self.infection_deck.restack_discard_pile()
                    break

                city_to_infect = card_drawn.get_city()
                colour_to_infect = city_to_infect.get_colour()
                self.add_cubes(city_to_infect, colour_to_infect, 1)

                if is_terminal():
                    reward += self.failure_reward
                    self.terminal = True
                    return self.get_current_state(), reward, True, info

            # Moving to next player
            self.action_points_left = PandemicGame.max_action_points
            self.current_turn += 1
            self.current_player = self.players[self.current_turn % self.player_count]

            if over_hand_limit():
                self.discard_card_phase = True

        return self.get_current_state(), reward, self.terminal, info

    def shuttle_flight(self, city):
        self.move_player(city)
        return

    def trade_card(self, player):
        self.action_points_left -= 1

        giving_player = self.current_player
        receiving_player = player

        if receiving_player.is_current_city_in_hand():
            giving_player = player
            receiving_player = self.current_player

        card_to_trade = giving_player.discard_current_city_card()
        receiving_player.add_to_hand(card_to_trade)
        return

    def treat_disease(self, colour):
        self.action_points_left -= 1

        city_to_treat_name = self.current_player.get_city().get_name()
        city_to_treat = self.cities[city_to_treat_name]

        cubes_to_remove = 1
        if self.cured[colour]:
            cubes_to_remove = city_to_treat.get_cubes(colour)

        self.remove_cubes(city_to_treat, colour, cubes_to_remove)
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

    def discard_current_city_card(self):
        return self.discard_card_by_name(self.__city.get_name())

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
        return

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
