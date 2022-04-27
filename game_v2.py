from city import City
from deck import Deck
from citycard import CityCard
from player import Player
from pathnode import PathNode
import json
import numpy as np


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
                 player_count=2, num_epidemics=4, use_research_stations=False):
        self.use_research_stations = use_research_stations
        self.cubes = None
        self.window = None
        self.colours = colours
        self.player_count = 2
        self.last_cured = {colour: False for colour in self.colours}

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
        self.state_shape = (self.num_cites * ((3 * num_colours) + (2 * self.player_count) + 2)) + \
                           (num_colours + player_count + 2)
        if self.use_research_stations:
            self.state_shape += self.num_cites

        # Defining Action space
        self.action_functions = {self.cure: {'name': 'cure', 'use_colour': True},
                                 self.give: {'name': 'give', 'use_colour': False},
                                 self.take: {'name': 'take', 'use_colour': False},
                                 self.treat: {'name': 'treat', 'use_colour': True}}
        if self.use_research_stations:
            self.action_functions[self.build] = {'name': 'build', 'use_colour': False}
        self.actions = []
        for function in self.action_functions:
            if self.action_functions[function]['name'] == 'cure':
                to_add = [[function, None, colour] for colour in self.colours]
            else:
                for colour in self.colours:
                    to_add = [[function, city_name] for city_name in self.city_names[colour]]
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
        self.num_epidemics = len(self.colours)
        self.epidemics_drawn = 0

        self.game_finished = True
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
        if self.num_outbreaks > 8:
            self.num_outbreaks = 8
        return

    def add_research_station(self, city):
        if city in self.research_stations:
            return
        city.set_has_res_station(True)
        self.research_stations.append(city)
        return

    def build(self, city_name):
        city = self.get_city_by_name(city_name)

        acting_player = self.players[self.current_turn]

        # Finding the shortest path to city
        hand = acting_player.get_hand().copy()
        has_card = False
        for card in hand:
            if card.has_city(city):
                used_card = card
                hand.remove(used_card)
                has_card = True
                break
        start_node = self.find_path(acting_player.get_city(), city, hand)

        # Moving Player
        action_points = 4
        action_points = self.move_player(acting_player, start_node, action_points)

        # Building research station if possible
        if action_points > 0 and has_card and \
                (acting_player.get_city().equals(city) and not city.has_research_station()):
            used_card = acting_player.discard_card_by_name(city_name)
            self.player_deck.discard_card(used_card)
            self.add_research_station(city)
            return True
        return False

    def can_take_action(self, action_name, city_name, colour):
        if city_name is not None:
            city = self.get_city_by_name(city_name)
        acting_player = self.players[self.current_turn]

        if action_name == 'build':  # Build: player needs city card in hand and no res station there
            return (not city.has_research_station()) and acting_player.is_city_in_hand(city)
        elif action_name == 'cure':  # Cure: player needs 5 or more colour of cards and res station at city
            return acting_player.can_cure(colour)
        elif action_name == 'give':  # give: player needs the city card in hand
            return acting_player.is_city_in_hand(city)
        elif action_name == 'take':  # take: another player needs to be at the city with the card
            for i in range(self.player_count):
                if i == self.current_turn:
                    continue
                other_player = self.players[i]
                if other_player.in_city(city) and other_player.is_city_in_hand(city):
                    return True
            return False
        elif action_name == 'treat':  # treat: city needs to have colour cubes on it
            return city.get_cubes(colour) > 0
        return None

    def cure(self, colour):
        acting_player = self.players[self.current_turn]
        hand = acting_player.get_hand().copy()

        # Getting cards to use to cure
        to_remove = []
        for card in hand:
            if card.has_colour(colour):
                to_remove.append(card)
        can_cure = len(to_remove) >= 5

        # Curing disease if possible
        if not can_cure or self.cure_tracker[colour]:
            return False
        for _ in range(5):
            card_to_remove = to_remove.pop()
            acting_player.discard_card_by_name(card_to_remove.get_name())
            self.player_deck.discard_card(card_to_remove)
        self.cure_tracker[colour] = True
        return True

    '''
    def cure(self, city_name, colour):
        city = self.get_city_by_name(city_name)
        acting_player = self.players[self.current_turn]

        # Finds path to city
        hand = acting_player.get_hand().copy()
        to_remove = []
        for card in hand:
            if card.has_colour(colour):
                to_remove.append(card)
        can_cure = len(to_remove) >= 5
        for card in to_remove:
            hand.remove(card)
        start_node = self.find_path(acting_player.get_city(), city, hand)

        # Moving Player
        action_points = 4
        action_points = self.move_player(acting_player, start_node, action_points)

        # Curing disease if possible
        if action_points <= 0 or not can_cure or self.cure_tracker[colour] or (
                not city.has_research_station()) or not acting_player.in_city(city):
            return False
        for _ in range(5):
            card_to_remove = to_remove.pop()
            acting_player.discard_card_by_name(card_to_remove.get_name())
            self.player_deck.discard_card(card_to_remove)
        self.cure_tracker[colour] = True
        return True
    '''

    def draw_player_cards(self, specify_cards=False):
        for _ in range(2):
            if not specify_cards:
                drawn_card = self.player_deck.draw_card()
            else:
                card_found = False
                while not card_found:
                    name = input("Enter card to draw or type 'empty' to indicate empty player deck")
                    if name == 'empty':
                        drawn_card = None
                        break
                    drawn_card = self.player_deck.get_card_by_name(name)
                    card_found = drawn_card is not None

            if drawn_card is None:
                return
            if drawn_card.is_epidemic:
                self.epidemic(specify_cards)
                continue
            self.players[self.current_turn].add_to_hand(drawn_card)
        return

    def epidemic(self, specify_card=False):
        self.inc_infection_rate()

        if not specify_card:
            infection_card = self.infection_deck.draw_bottom_card()
        else:
            card_found = False
            while not card_found:
                name = input("Enter name of city to infect or 'empty' to indicate an empty deck:\n")

                if name == 'empty':
                    infection_card = None
                    break

                infection_card = self.infection_deck.get_card_by_name(name)
                card_found = infection_card is not None

        if infection_card is not None:
            self.infection_deck.discard_card(infection_card)
            infected_city = self.get_city_by_name(infection_card.get_name())
            self.add_cubes(infected_city, infected_city.get_colour(), 3)
        self.infection_deck.restack_discard_pile()

        self.epidemics_drawn += 1
        return

    def fill_connected_cities(self, city):
        connected_names = self.game_data[city.get_colour()][city.get_name()]
        connected_cities = []
        for name in connected_names:
            city_to_add = self.get_city_by_name(name)
            if city_to_add is not None:
                connected_cities.append(city_to_add)
        city.set_connected_cities(connected_cities)
        return

    def find_move_after_state(self, current_node, action_points):
        after_state = self.get_state_dict()
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            card_used = current_node.get_used_card()
            if card_used is not None:
                after_state['city_cards']['player_hands'][self.current_turn].remove(card_used)
                after_state['city_cards']['discarded'].append(card_used)
            action_points -= 1
        after_state['player_locations'][self.current_turn] = current_node.get_city()
        return after_state, action_points

    def find_path(self, start_city, end_city, cards_to_use=[]):
        # Uses graph search to find path
        start_node = PathNode(start_city, 0)
        if start_city.equals(end_city):
            return start_node
        frontier = [start_node]
        path_found = False
        while not path_found:
            current_node = frontier.pop(0)
            cost = current_node.get_cost() + 1
            if cost > 4:
                end_node = to_add
                break

            # By moving
            action = 'move'
            for city in current_node.get_connected_cities():
                to_add = PathNode(city, cost, current_node, action)
                frontier.append(to_add)
                if to_add.get_city().equals(end_city):
                    path_found = True
                    end_node = to_add
                    break
            if path_found:
                break
            # Shuttle flight
            action = 'shuttle'
            if current_node.has_research_station():
                for city in self.research_stations:
                    to_add = PathNode(city, cost, current_node, action)
                    frontier.append(to_add)
                    if to_add.get_city().equals(end_city):
                        path_found = True
                        end_node = to_add
                        break
            if path_found:
                break
            # Charter_flight
            action = 'charter'
            for card in cards_to_use:
                if card.has_name(current_node.get_name()) and not current_node.card_in_node_path(card):
                    end_node = PathNode(end_city, cost, current_node, action, used_card=card)
                    frontier.append(end_node)
                    path_found = True
                    break
            if path_found:
                break
            action = 'direct'
            # Direct Flight
            for card in cards_to_use:
                if not current_node.card_in_node_path(card):
                    to_add = PathNode(card.get_city(), cost, current_node, action, used_card=card)
                    frontier.append(to_add)
                    if to_add.get_city().equals(end_city):
                        path_found = True
                        end_node = to_add
                        break

        # Generating path from end_node
        finished_path = False
        current_node = end_node
        while not finished_path:
            prev_node = current_node.get_previous_node()
            prev_node.set_next_node(current_node)
            prev_node.set_action_to_get_to_next(current_node.get_arriving_action())
            current_node = prev_node
            finished_path = current_node.get_city().equals(start_city)

        return prev_node

    def get_actions_and_after_states(self):
        possible_actions = [i for i in range(self.action_space)
                            if self.can_take_action(self.action_functions[self.actions[i][0]]['name'],
                                                    self.actions[i][1],
                                                    self.actions[i][2])]

        after_states = [self.get_after_state(action) for action in possible_actions]

        num_possible_actions = len(possible_actions)
        i = 0
        while i < num_possible_actions:
            if after_states[i] is None:
                del possible_actions[i]
                del after_states[i]
                num_possible_actions -= 1
                continue
            i += 1
        return possible_actions, after_states

    def get_action_shape(self):
        return self.action_space

    def get_action_type(self, action_index):
        action = self.actions[action_index]
        func = action[0]

        return self.action_functions[func]['name']

    def get_after_state(self, action_index):
        action = self.actions[action_index]

        action_name = self.action_functions[action[0]]['name']
        if action_name[1] is not None:
            city = self.get_city_by_name(action[1])
        colour = action[2]

        acting_player = self.players[self.current_turn]

        # Getting hand of cards that can be used to move
        hand = acting_player.get_hand().copy()
        if action_name in ['build', 'give']:  # Cannot use chosen city card
            for card in hand:
                if card.has_city(city):
                    used_card = card
                    hand.remove(card)
                    break
        elif action_name == 'cure':  # Cannot use cards of chosen colour
            to_remove = []
            for card in hand:
                if card.has_colour(colour):
                    to_remove.append(card)
            for card in to_remove:
                hand.remove(card)

        # Moving Player
        action_points = 4
        if not action_name == 'cure':
            start_node = self.find_path(acting_player.get_city(), city, hand)
        else:
            player_city = acting_player.get_city()
            start_node = self.find_path(player_city, player_city , hand)
        after_state, action_points = self.find_move_after_state(start_node, action_points)

        # Performing action
        if action_points > 0:
            if action_name == 'build':
                after_state['research_stations'].append(city)
                after_state['city_cards']['player_hands'][self.current_turn].remove(used_card)
                after_state['city_cards']['discarded'].append(used_card)
            elif action_name == 'cure':
                after_state['cured_diseases'].append(colour)
                cards_to_cure = 5
                while cards_to_cure > 0:
                    card_to_remove = to_remove.pop()
                    after_state['city_cards']['player_hands'][self.current_turn].remove(card_to_remove)
                    after_state['city_cards']['discarded'].append(card_to_remove)
                    cards_to_cure -= 1
            elif action_name == 'give':
                player_index = None
                for i in range(self.player_count):
                    if i == self.current_turn:
                        continue
                    if self.players[i].in_city(city):
                        player_index = i
                        break
                if player_index is not None:
                    after_state['city_cards']['player_hands'][self.current_turn].remove(used_card)
                    after_state['city_cards']['player_hands'][player_index].append(used_card)
            elif action_name == 'take':
                player_index = None
                for i in range(self.player_count):
                    if player_index is not None:
                        break
                    if i == self.current_turn:
                        continue
                    for card in self.players[i].get_hand():
                        if card.has_city(city):
                            receiving_card = card
                            player_index = i
                            break
                if player_index is not None:
                    after_state['city_cards']['player_hands'][player_index].remove(receiving_card)
                    after_state['city_cards']['player_hands'][self.current_turn].append(receiving_card)
            elif action_name == 'treat':
                num_cubes = city.get_cubes(colour)
                if self.cure_tracker[colour]:
                    new_num_cubes = 0
                else:
                    new_num_cubes = num_cubes - action_points
                after_state['infected_cities'][colour][num_cubes].remove(city)
                if new_num_cubes > 0:
                    after_state['infected_cities'][colour][new_num_cubes].append(city)
        else:  # If action points are 0 or less player cannot move to space in time to perform action so return None
            return None

        # Converting after_state dict into numpy array
        after_state = self.state_dict_to_state(after_state)

        return after_state

    def get_action_string(self, action_index):
        # Finding action
        action = self.actions[action_index]
        func = action[0]
        city_name = action[1]
        colour_used = action[2]

        print_str = self.action_functions[func]['name']
        if city_name is not None:
            print_str += " at " + city_name
        if colour_used is not None:
            print_str += " with " + colour_used
        return print_str

    def get_city_by_name(self, name):
        for city in self.cities:
            if city.has_name(name):
                return city
        return None

    def get_current_state(self):
        state = np.zeros(self.state_shape)

        # Current Turn
        state[self.current_turn] = 1.0
        index = self.player_count

        for city in self.cities:
            # Cubes on cities
            for colour in self.colours:
                for num_cubes in range(1, 4):
                    if city.get_cubes(colour) == num_cubes:
                        state[index] = 1.0
                    index += 1

            if self.use_research_stations:
                # Has research station
                state[index] = float(city.has_research_station())
                index += 1

            # City card location
            for player in self.players:
                state[index] = float(player.is_city_in_hand(city))
                index += 1
            state[index] = float(self.player_deck.city_in_discard_pile(city))
            index += 1

            # Infection card in discard pile
            state[index] = float(self.infection_deck.city_in_discard_pile(city))
            index += 1

            # Has player there
            for player in self.players:
                state[index] = float(player.in_city(city))
                index += 1

        # Number of Outbreaks
        if self.num_outbreaks == 0:
            state[index] = 0.0
        else:
            state[index] = float(self.num_outbreaks / 8)
        index += 1

        # Epidemics drawn
        if self.epidemics_drawn == 0:
            state[index] = 0.0
        else:
            state[index] = float(self.epidemics_drawn / self.num_epidemics)
        index += 1

        # Cured Diseases
        for colour in self.colours:
            state[index] = float(self.cure_tracker[colour])
            index += 1

        return state

    def get_state_dict(self):
        state = {'current_turn': self.current_turn, 'infected_cities': {colour: {i: [city for city in self.cities
                                                                                     if city.get_cubes(colour) == i]
                                                                                 for i in range(1, 4)} for colour in
                                                                        self.colours}, 'outbreaks': self.num_outbreaks,
                 'research_stations': self.research_stations.copy(),
                 'player_locations': [player.get_city() for player in self.players],
                 'city_cards': {'player_hands': [player.get_hand().copy() for player in self.players],
                                'discarded': self.player_deck.get_discard_pile().copy()},
                 'infection_cards': self.infection_deck.get_discard_pile().copy(), 'epidemics': self.epidemics_drawn,
                 'cured_diseases': [colour for colour in self.colours if self.cure_tracker[colour]]}

        return state

    def get_state_shape(self):
        return self.state_shape

    def give(self, city_name):
        city = self.get_city_by_name(city_name)
        acting_player = self.players[self.current_turn]

        # Finding path to city
        hand = acting_player.get_hand().copy()
        has_card = False
        for card in hand:
            if card.has_city(city):
                giving_card = card
                hand.remove(giving_card)
                has_card = True
                break
        start_node = self.find_path(acting_player.get_city(), city, hand)

        # Moving Player
        action_points = 4
        action_points = self.move_player(acting_player, start_node, action_points)

        # Gives card to another player if possible
        for i in range(self.player_count):
            if i == self.current_turn:
                continue
            receiving_player = self.players[i]
        if action_points <= 0 or (not has_card) or (not receiving_player.in_city(city)) or (
                (not acting_player.in_city(city))):
            return False
        giving_card = acting_player.discard_card_by_name(city_name)
        receiving_player.add_to_hand(giving_card)
        return True

    def inc_infection_rate(self):
        if self.infection_rate_index < len(Game.infection_rate_track) - 1:
            self.infection_rate_index += 1
        return

    def infect_cities(self, specify_card=False):
        for _ in range(Game.infection_rate_track[self.infection_rate_index]):
            self.set_cities_to_no_outbreaks()

            if not specify_card:
                infection_card = self.infection_deck.draw_card()
            else:
                card_found = False
                while not card_found:
                    name = input("Enter name of city to infect or 'empty' to indicate an empty deck:\n")

                    if name == 'empty':
                        card_found = True
                        infection_card = None
                        break

                    infection_card = self.infection_deck.get_card_by_name(name)
                    card_found = infection_card is not None

            # If out of infection cards, increases the infection rate and restack the deck
            if infection_card is None:
                self.infection_deck.restack_discard_pile()
                self.inc_infection_rate()
                return

            self.infection_deck.discard_card(infection_card)
            infected_city = self.get_city_by_name(infection_card.get_name())
            self.add_cubes(infected_city, infected_city.get_colour(), 1)
        return

    def is_terminal(self):
        # Win if all disease cured
        all_cured = True
        for colour in self.colours:
            if not self.cure_tracker[colour]:
                all_cured = False
                break
        if all_cured:
            return True, True, 'win'

        # Loss if: outbreaks >= 8, more than 24 cubes of a single colour, run out of player cards
        if self.num_outbreaks >= 8:
            return True, False, 'outbreaks'
        '''
        if len(self.colours) > 1:
            if self.player_deck.get_number_of_cards() <= 0:
                return True, False, 'player_cards'
        '''
        for colour in self.colours:
            if self.cubes[colour] > 24:
                return True, False, 'disease_cubes'

        # Otherwise Game is not terminal
        return False, False, None

    def move_player(self, moving_player, current_node, action_points):
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            card_used = current_node.get_used_card()
            if card_used is not None:
                moving_player.discard_card_by_name(card_used.get_name())
                self.player_deck.discard_card(card_used)
            action_points -= 1
        moving_player.move_to(current_node.get_city())
        return action_points

    def print_current_state(self):
        # Infected Cities
        infected_cities = {colour: {i: [city.get_name() for city in self.cities if city.get_cubes(colour) == i]
                                    for i in range(1, 4)} for colour in self.colours}
        print("Infected cities:")
        for colour in self.colours:
            print(colour)
            for i in range(1, 4):
                print(str(i) + ": " + str(infected_cities[colour][i]))

        # Number of cubes
        print('cube count')
        for colour in self.colours:
            print(colour + " cubes: " + str(self.cubes[colour]))

        # Outbreaks
        print("Outbreaks\n" + str(self.num_outbreaks))

        if self.use_research_stations:
            # Research stations
            print("Research stations")
            res_str = ""
            for city in self.research_stations:
                res_str += (city.get_name() + " ")
            print(res_str)

        # Player locations
        print("Player locations")
        for player in self.players:
            print(player.get_city().get_name())

        # Player hands
        print("Player hands")
        for player in self.players:
            hand_str = ""
            for card in player.get_hand():
                hand_str += (card.get_name() + " ")
            print(hand_str)

        # Infection cards in discard pile
        print("Infection discard pile")
        infection_str = ""
        for card in self.infection_deck.get_discard_pile():
            infection_str += (card.get_name() + " ")
        print(infection_str)

        # Number of epidemics drawn
        print("Number of epidemics\n" + str(self.epidemics_drawn))

        # Cured diseases
        print("Cured diseases")
        for colour in self.colours:
            if self.cure_tracker[colour]:
                print(colour)
        return

    def reset(self, specify_sate=False):
        # New Cities
        self.cities = []
        for colour in self.colours:
            city_names = self.game_data[colour]
            self.cities += [City(city_name, colour) for city_name in city_names]
        for city in self.cities:
            self.fill_connected_cities(city)

        # New Player and Infection Deck
        self.player_deck = Deck()
        self.infection_deck = Deck()
        for city in self.cities:
            self.infection_deck.add_card(CityCard(city))
            self.player_deck.add_card(CityCard(city))
        self.infection_deck.shuffle()
        self.player_deck.shuffle()

        # Cure tracker
        self.last_cured = {colour: False for colour in self.colours}
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
        if self.use_research_stations:
            self.add_research_station(start_city)

        # New Players
        self.players = [Player(str(i), city=start_city) for i in range(self.player_count)]

        # New Player hands
        cards_per_player = (6 - self.player_count)
        if not specify_sate:
            for player in self.players:
                for _ in range(cards_per_player):
                    card_to_draw = self.player_deck.draw_card()
                    player.add_to_hand(card_to_draw)
        else:
            for player in self.players:
                for _ in range(cards_per_player):
                    card_to_draw = None
                    while card_to_draw is None:
                        name = input("Choose a card to give to " + player.get_name() + " :\n")
                        card_to_draw = self.player_deck.get_card_by_name(name)
                    player.add_to_hand(card_to_draw)

        # New Current turn
        self.current_turn = 0

        # New epidemics
        self.player_deck.add_epidemics(self.num_epidemics)
        self.epidemics_drawn = 0

        # Infect new cities
        self.cubes = {colour: 0 for colour in self.colours}
        for cubes_to_place in range(1, 4):
            for _ in range(3):
                if not specify_sate:
                    city_name = self.infection_deck.draw_and_discard().get_name()
                else:
                    city_card = None
                    while city_card is None:
                        city_name = input("Choose a city to infect with " + str(cubes_to_place) + " cubes:\n")
                        city_card = self.infection_deck.get_card_by_name(city_name)
                    self.infection_deck.discard_card(city_card)

                city = self.get_city_by_name(city_name)
                self.add_cubes(city, city.get_colour(), cubes_to_place)

        self.game_finished = False
        state = self.get_current_state()
        return state

    def set_cities_to_no_outbreaks(self):
        for city in self.cities:
            city.set_has_outbreaked(False)
        return

    def state_dict_to_state(self, state_dict):
        state = np.zeros(self.state_shape)

        state[state_dict['current_turn']] = 1.0
        index = self.player_count

        for city in self.cities:
            # Cubes on cities
            infected_cities = state_dict['infected_cities']
            for colour in self.colours:
                for num_cubes in range(1, 4):
                    state[index] = float(city in infected_cities[colour][num_cubes])
                    index += 1

            if self.use_research_stations:
                # Has research station
                state[index] = float(city in state_dict['research_stations'])
                index += 1

            # City card locations
            city_card_found = False
            city_cards = state_dict['city_cards']
            for i in range(self.player_count):
                for card in city_cards['player_hands'][i]:
                    if city_card_found:
                        break
                    if card.has_city(city):
                        state[index] = 1.0
                        city_card_found = True
                        break
                index += 1
            if not city_card_found:
                for card in city_cards['discarded']:
                    if card.has_city(city):
                        state[index] = 1.0
                        break
            index += 1

            # Infection card in discard pile
            infection_cards = state_dict['infection_cards']
            for card in infection_cards:
                if card.has_city(city):
                    state[index] = 1.0
                    break
            index += 1

            # Has player there
            for i in range(self.player_count):
                state[index] = float(city.equals(state_dict['player_locations'][i]))
                index += 1

        # Number of outbreaks
        if state_dict['outbreaks'] == 0:
            value = 0.0
        else:
            value = float(state_dict['outbreaks'] / 8)
        state[index] = value
        index += 1

        # Epidemics seen
        if state_dict['epidemics'] == 0:
            value = 0.0
        else:
            value = float(state_dict['epidemics']/ self.num_epidemics)
        state[index] = value
        index += 1

        # Cured diseases
        for colour in self.colours:
            state[index] = float(colour in state_dict['cured_diseases'])
            index += 1

        return state

    def step(self, action_index, print_action=False, specify_state=False):
        if self.game_finished:
            print("Must call reset before invoking step")

        # Finding action
        action = self.actions[action_index]
        func = action[0]
        city_name = action[1]
        colour_used = action[2]

        # Taking action
        print_str = self.action_functions[func]['name']
        if city_name is not None:
            print_str += " at " + city_name
        if colour_used is None:
            action_successful = func(city_name)
        else:
            if city_name is not None:
                action_successful = func(city_name, colour_used)
            else:
                action_successful = func(colour_used)
            print_str += " with " + colour_used
        if print_action:
            print(print_str)

        # Transitioning to next State
        self.draw_player_cards(specify_state)
        self.infect_cities(specify_state)
        self.current_turn = (self.current_turn + 1) % self.player_count

        # Finding next state
        next_state = self.get_current_state()

        # Finding if state is terminal
        terminal, win, reason = self.is_terminal()

        # Finding reward: +1 for each turn, -10 for loss, +10 for curing a disease
        reward = 1.0
        for colour in self.colours:
            if self.cure_tracker[colour] and not self.last_cured[colour]:
                reward += 10.0
        if terminal and not win:
            reward += -10.0
        self.game_finished = terminal
        for colour in self.colours:
            self.last_cured[colour] = self.cure_tracker[colour]

        info = {'cured_diseases': [colour for colour in self.colours if self.cure_tracker[colour]],
                'terminal_reason': reason}
        return next_state, reward, terminal, info

    def take(self, city_name):
        city = self.get_city_by_name(city_name)
        acting_player = self.players[self.current_turn]

        # Finding path to city
        start_node = self.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Moving Player
        action_points = 4
        action_points = self.move_player(acting_player, start_node, action_points)

        # Taking card, if possible
        # Checks if there is a player in that city and if they have the corresponding city card in hand
        giving_player = None
        for i in range(self.player_count):
            player = self.players[i]
            if (not player.equals(acting_player)) and player.is_current_city_in_hand() and player.in_city(city):
                giving_player = player
                break
        if action_points <= 0 or giving_player is None or (
                not acting_player.in_city(city)):
            return False
        card_to_take = giving_player.discard_card_by_name(city_name)
        acting_player.add_to_hand(card_to_take)
        return True

    def treat(self, city_name, colour):
        city = self.get_city_by_name(city_name)
        acting_player = self.players[self.current_turn]

        # Finding path to city
        start_node = self.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Moving Player
        action_points = 4
        action_points = self.move_player(acting_player, start_node, action_points)

        # Removing as many cubes as possible
        if city.get_cubes(colour) <= 0 or action_points <= 0 or not acting_player.in_city(city):
            return False
        new_cubes = city.get_cubes(colour) - action_points
        cubes_removed = action_points
        if new_cubes < 0 or self.cure_tracker[colour]:
            cubes_removed = city.get_cubes(colour)
            new_cubes = 0
        self.cubes[colour] -= cubes_removed
        city.set_cubes(colour, new_cubes)
        return True
