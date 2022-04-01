import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from learningagent import LearningAgent
from game import Game
import random as rand
import numpy as np

''' State details:
for each city:
    blue cubes:
        has 1 cubes
        has 2 cubes
        has 3 cubes
    yellow cubes:
        has 1 cubes
        has 2 cubes
        has 3 cubes
    black cubes:
        has 1 cubes
        has 2 cubes
        has 3 cubes1
    red cubes:
        has 1 cubes
        has 2 cubes
        has 3 cubes

    has research station

    for city card:
        in player 1-n hand
        in discard pile

    if infection card in discard pile

    has player 1-n there

num outbreaks: 0-8

epidemics in deck: 0-4

for each colour:
    is cured

# total inputs:
48 cities: 48 * (12 + 1 + (player_count + 1) + 1 + player_count)
other inputs: 1 + 1 + 4
total: 726 + 96*player_count

### Actions after_state

Treat(city, colour) : if city has colour disease cubes, move to it and remove as many cubes as possible
Discover_Cure(city, colour) : if city has research station and player can cure colour, move to city and cure disease
Build(city) : if player has city card, move to that city and build research station
Give(city) : if a player has that city card, go to that city and if another player is there give the card
Take(city) : if another player has a city card and is in that city, go to that city and take the card

### Rewards
+1 for each turn
+10 for curing a disease
-10 for game loss
'''


class DQNAgent(LearningAgent):
    learning_file = 'dqn/dqn_learning_data.json'
    results_file = 'results/dqn_results.json'

    colours = Game.colours

    def __init__(self, game, window, start_city, initialise=True, player_count=2,
                 alpha=0.0001, gamma=0.9, epsilon=0.1,
                 net_layers=[64], memory_size=10000, batch_size=32):
        super(DQNAgent, self).__init__(game, DQNAgent.learning_file, DQNAgent.results_file,
                                       player_count, window, start_city)

        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.net_layers = net_layers
        self.num_net_layers = len(self.net_layers)
        self.state_shape = 726 + (96 * self.player_count)
        self.current_state = {}
        self.turn_count = 0
        self.batch_size = batch_size

        self.cities = self.game.get_cities()

        num_cities = len(self.cities)
        self.action_functions = {self.build: {'name': 'build', 'use_colour': False},
                                 self.cure: {'name': 'cure', 'use_colour': True},
                                 self.give: {'name': 'give', 'use_colour': False},
                                 self.take: {'name': 'take', 'use_colour': False},
                                 self.treat: {'name': 'treat', 'use_colour': True}}
        self.actions = []
        for action in self.action_functions:
            to_add = [[action, city] for city in self.cities]
            if not self.action_functions[action]['use_colour']:
                for elm in to_add:
                    elm.append(None)
            else:
                new_to_add = [elm + [colour] for elm in to_add for colour in self.colours]
                to_add = new_to_add
            self.actions += to_add
        self.num_actions = (3 * num_cities) + (2 * num_cities * len(DQNAgent.colours))
        self.memory = []
        self.memory_size = memory_size

        self.net = None
        self.build_neural_net(initialise)
        return

    # TODO: add action functions

    def act(self, print_action=False):
        # Chooses action
        action_index = self.choose_action()
        action = self.actions[action_index]

        # Finds after state
        city_used = action[1]
        colour_used = action[2]
        if colour_used is None:
            after_state = action[0](self, city_used)
        else:
            after_state = action[0](self, city_used, colour_used)

        # Transitions to after state
        action_str = self.action_functions[action]['name']
        # Moving Players
        for i in range(self.player_count):
            self.players[i].move_to(after_state['player_locations'][i])
        # Updating Player Hands
        for i in range(self.player_count):
            new_hand = after_state['city_cards']['player_hands'][i]
            for card in new_hand:
                if card not in self.players[i].get_hand():
                    self.players[i].add_to_hand(card)
            hand_len = len(self.players[i].get_hand())
            k = 0
            while k < hand_len:
                card = self.players[i].get_hand()[k]
                if card not in new_hand:
                    self.players[i].discard_card_by_name(card.get_name())
                    hand_len -= 1
                    continue
                k += 1
        # Adjusting state
        if action_str == 'build':
            city_used.set_has_res_station(city_used in after_state['research_stations'])
            return
        if action_str == 'cure':
            if colour_used in after_state['cured_diseases']:
                self.game.cure_disease(colour_used)
            return
        if action_str == 'treat':
            new_cube_count = 0
            for i in range(1, 4):
                if city_used in after_state['infected_cities'][colour_used][i]:
                    new_cube_count = i
                    break
            city_used.set_cubes(colour_used, new_cube_count)
            return
        return

    def build(self, city):
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
        start_node = self.game.find_path(acting_player.get_city(), city, hand)

        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0 or not has_card:
            return after_state
        after_state['research_stations'].append(city)
        after_state['city_cards']['player_hands'][self.current_turn].remove(used_card)
        after_state['city_cards']['discarded'].append(used_card)
        return after_state

    def build_neural_net(self, initialise):
        self.net = keras.Sequential()
        if initialise:
            self.net.add(Dense(units=self.net_layers[0],
                               activation='relu',
                               input_dim=self.state_shape))
            for i in range(1, self.num_net_layers):
                self.net.add(Dense(units=self.net_layers[i],
                                   activation='relu'))
            self.net.add(Dense(units=self.num_actions, activation='linear'))
            self.net.compile(optimizer=tf.keras.optimizers.Adam(lr=self.alpha),
                             loss='mse',
                             metrics=['mae', 'mse'])
        else:
            print("Cannot load data from file")
            return
            # TODO: add load net from file
        self.net.summary()
        return

    def choose_action(self):
        possible_actions = []
        acting_player = self.players[self.current_turn]

        if rand.uniform(0, 1) < self.epsilon:  # Takes random action
            return rand.randint(0, self.num_actions)

        net_input = self.state_to_net_input(self.current_state)
        q_out = self.q_net(net_input.reshape(1, self.state_shape))
        return np.argmax(q_out)

    def cure(self, city, colour):
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
        start_node = self.game.find_path(acting_player.get_city(), city, hand)

        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        # Checks if agent can cure at the city after arriving
        if (action_points <= 0) or (not can_cure) or not city.has_research_station():
            return after_state
        after_state['cured_diseases'].append(colour)
        cards_to_cure = 5
        while cards_to_cure > 0:
            card_to_remove = to_remove.pop()
            after_state['city_cards']['player_hands'][self.current_turn].remove(card_to_remove)
            after_state['city_cards']['discarded'].append(card_to_remove)
            cards_to_cure -= 1
        return after_state

    def give(self, city):
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
        start_node = self.game.find_path(acting_player.get_city(), city, hand)

        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        # Checks if agent can give card
        if action_points <= 0 or not has_card:
            return after_state
        player_index = -1
        for i in range(self.player_count):
            receiving_player = self.players[i]
            if (not receiving_player.equals(acting_player)) and (receiving_player.in_city(city)):
                player_index = i
                break
        if player_index == -1:
            return after_state
        after_state['city_cards']['player_hands'][self.current_turn].remove(giving_card)
        after_state['city_cards']['player_hands'][player_index].append(giving_card)
        return after_state

    # Add learn
    def learn(self, terminal):
        return

    # TODO: build agent reset
    def reset(self):
        return

    # Add saving trajectory
    def save_trajectory(self, terminal):
        return

    def set_current_state(self):
        # Infected Cities
        self.current_state['infected_cities'] = {colour: {i: [city for city in self.cities
                                                              if city.get_cubes(colour) == i]
                                                          for i in range(1, 4)} for colour in DQNAgent.colours}

        # Number of outbreaks
        self.current_state['outbreaks'] = self.game.get_outbreaks()

        # Research stations
        self.current_state['research_stations'] = self.game.get_research_stations()

        # Player locations
        self.current_state['player_locations'] = [player.get_city() for player in self.players]

        # City card locations
        self.current_state['city_cards'] = {'player_hands': [[] for player in self.players], 'discarded': []}
        for card in self.game.get_discarded_city_cards():
            card_added = False
            for i in range(self.player_count):
                if self.players[i].has_card(card):
                    self.current_state['city_cards']['player_hands'][i].append(card)
                    card_added = True
                    break
            if not card_added:
                self.current_state['city_cards']['discarded'].append(card)

        # Infection Cards in discard pile
        self.current_state['infection_cards'] = self.game.get_infection_discard_pile()

        # Number of epidemics drawn
        self.current_state['epidemics'] = self.game.get_epidemics()

        # Cured diseases
        self.current_state['cured_diseases'] = [colour for colour in DQNAgent.colours if self.game.is_cured(colour)]
        return

    def state_to_net_input(self, state):
        net_input = [0.0 for i in range(self.state_shape)]

        index = 0
        for city in self.cities:
            # Cubes on cities
            infected_cities = state['infected_cities']
            for colour in Game.colours:
                for num_cubes in range(1, 4):
                    net_input[index] = float(city in infected_cities[colour][num_cubes])
                    index += 1

            # Has research station
            net_input[index] = float(city in state['research_stations'])
            index += 1

            # City card locations
            city_card_found = False
            city_cards = state['city_cards']
            for i in range(self.player_count):
                for card in city_cards['player_hands'][i]:
                    if city_card_found:
                        break
                    if card.has_city(city):
                        net_input[index] = 1.0
                        city_card_found = True
                        break
                index += 1
            if not city_card_found:
                for card in city_cards['discarded']:
                    if card.has_city(city):
                        net_input[index] = 1.0
                        break
            index += 1

            # Infection card in discard pile
            infection_cards = state['infection_cards']
            for card in infection_cards:
                if card.has_city(city):
                    net_input[index] = 1.0
                    break
            index += 1

            # Has player there
            for i in range(self.player_count):
                net_input[index] = float(city.equals(state['player_locations'][i]))
                index += 1

        # Number of outbreaks
        if state['outbreaks'] == 0:
            value = 0.0
        else:
            value = float(1.0 / state['outbreaks'])
        net_input[index] = value
        index += 1

        # Epidemics seen
        if state['epidemics'] == 0:
            value = 0.0
        else:
            value = float(1.0 / state['epidemics'])
        net_input[index] = value
        index += 1

        # Cured diseases
        for colour in Game.colours:
            net_input[index] = float(colour in state['cured_diseases'])
            index += 1

        return np.array([net_input])

    # Add transitioning to next state, THIS NEXT
    def transition(self, terminal):
        return

    def take(self, city):
        acting_player = self.players[self.current_turn]

        # Checks if there is a player in that city and if they have the corresponding city card in hand
        giving_player_index = None
        giving_player = None
        for i in range(self.player_count):
            player = self.players[i]
            if (not player.equals(acting_player)) and player.is_current_city_in_hand() and player.in_city(city):
                giving_player_index = i
                giving_player = player
                break

        # Finding path to city
        start_node = self.game.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Working out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        # Checks if it can take the card
        if action_points <= 0 or giving_player_index is None:
            return after_state
        for card in giving_player.get_hand():
            if card.has_city(city):
                taking_card = card
                break
        after_state['city_cards']['player_hands'][giving_player_index].remove(taking_card)
        after_state['city_cards']['player_hands'][self.current_turn].append(taking_card)
        return after_state

    def treat(self, city, colour):
        acting_player = self.players[self.current_turn]

        # Finding path to city
        start_node = self.game.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Working out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        num_cubes = city.get_cubes(colour)
        if action_points <= 0 or num_cubes <= 0:
            return after_state
        if self.game.is_cured(colour):
            after_state['infected_cities'][colour][num_cubes].remove(city)
            return after_state
        new_num_cubes = num_cubes - action_points
        after_state['infected_cities'][colour][num_cubes].remove(city)
        if new_num_cubes > 0:
            after_state['infected_cities'][colour][new_num_cubes].append(city)
        return after_state

