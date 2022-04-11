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
                 player_count=2, num_epidemics=4):
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
        self.state_shape = (self.num_cites * ((3 * num_colours) + (2 * self.player_count) + 3)) + \
                           (num_colours + player_count + 2)

        # Defining Action space
        self.action_functions = {self.build: {'name': 'build', 'use_colour': False},
                                 self.cure: {'name': 'cure', 'use_colour': True},
                                 self.give: {'name': 'give', 'use_colour': False},
                                 self.take: {'name': 'take', 'use_colour': False},
                                 self.treat: {'name': 'treat', 'use_colour': True}}
        self.actions = []
        for function in self.action_functions:
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

    def draw_player_cards(self):
        for _ in range(2):
            drawn_card = self.player_deck.draw_card()
            if drawn_card is None:
                return
            if drawn_card.is_epidemic:
                self.epidemic()
                continue
            self.players[self.current_turn].add_to_hand(drawn_card)
        return

    def epidemic(self):
        self.inc_infection_rate()

        infection_card = self.infection_deck.draw_bottom_card()
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

    def get_action_shape(self):
        return self.action_space

    # Add get after state
    def get_after_state(self, action):
        after_state = None
        return after_state

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

    def infect_cities(self):
        for _ in range(Game.infection_rate_track[self.infection_rate_index]):
            self.set_cities_to_no_outbreaks()

            infection_card = self.infection_deck.draw_card()

            # If out of infection cards, increases the infection rate and restacks the deck
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
        if len(self.colours) > 1:
            if self.player_deck.get_number_of_cards() <= 0:
                return True, False, 'player_cards'
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

        # Outbreaks
        print("Outbreaks\n" + str(self.num_outbreaks))

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

    def reset(self):
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
        self.add_research_station(start_city)

        # New Players
        self.players = [Player(str(i), city=start_city) for i in range(self.player_count)]

        # New Player hands
        cards_per_player = (6 - self.player_count)
        for player in self.players:
            for _ in range(cards_per_player):
                card_to_draw = self.player_deck.draw_card()
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
                city = self.get_city_by_name(self.infection_deck.draw_and_discard().get_name())
                self.add_cubes(city, city.get_colour(), cubes_to_place)

        self.game_finished = False
        state = self.get_current_state()
        return state

    def set_cities_to_no_outbreaks(self):
        for city in self.cities:
            city.set_has_outbreaked(False)
        return

    def step(self, action_index, print_action=False):
        if self.game_finished:
            print("Must call reset before invoking step")

        # Finding action
        action = self.actions[action_index]
        func = action[0]
        city_name = action[1]
        colour_used = action[2]

        # Taking action
        print_str = self.action_functions[func]['name'] + " at " + city_name
        if colour_used is None:
            action_successful = func(city_name)
        else:
            action_successful = func(city_name, colour_used)
            print_str += " with " + colour_used
        if print_action:
            print(print_str)

        # Transitioning to next State
        self.draw_player_cards()
        self.infect_cities()
        self.current_turn = (self.current_turn + 1) % self.player_count

        # Finding next state
        next_state = self.get_current_state()

        # Finding if state is terminal
        terminal, win, reason = self.is_terminal()

        # Finding reward: +1 for each turn, -10 for loss, +10 for curing a disease
        reward = 1
        for colour in self.colours:
            if self.cure_tracker[colour] and not self.last_cured[colour]:
                reward += 10
        if terminal and not win:
            reward += -10
        self.game_finished = terminal
        for colour in self.colours:
            self.last_cured[colour] = self.cure_tracker[colour]

        info = {'terminal_reason': reason}
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
        if new_cubes < 0 or self.cure_tracker[colour]:
            new_cubes = 0
        city.set_cubes(colour, new_cubes)
        return True
