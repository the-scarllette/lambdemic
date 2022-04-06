import math

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


def copy_state(to_copy):
    new_state = {'infected_cities': {colour: {i: [city for city in to_copy['infected_cities'][colour][i]]
                                              for i in range(1, 4)} for colour in Game.colours},
                 'outbreaks': to_copy['outbreaks'],
                 'research_stations': [city for city in to_copy['research_stations']],
                 'player_locations': [city for city in to_copy['player_locations']],
                 'city_cards': {'player_hands': [[card for card in player_hand]
                                                 for player_hand in to_copy['city_cards']['player_hands']],
                                'discarded': [card for card in to_copy['city_cards']['discarded']]},
                 'infection_cards': [card for card in to_copy['infection_cards']], 'epidemics': to_copy['epidemics'],
                 'cured_diseases': [colour for colour in to_copy['cured_diseases']]}

    return new_state


def reward_function(state, next_state, terminal):
    reward = DQNAgent.turn_reward

    for colour in next_state['cured_diseases']:
        if colour not in state['cured_diseases']:
            reward += DQNAgent.cure_reward

    if terminal and len(next_state['cured_diseases']) < 4:
        reward += DQNAgent.lose_game_reward

    return reward


class DQNAgent(LearningAgent):
    learning_file = 'dqn/dqn_learning_data.json'
    results_file = 'results/dqn_results.json'

    colours = Game.colours

    turn_reward = 0
    cure_reward = 1
    lose_game_reward = -1

    def __init__(self, game, window, start_city, initialise=True, target_network=False, target_update_count=32,
                 mask_action_values=True,
                 player_count=2, alpha=0.0001, gamma=0.9, epsilon=0.1,
                 net_layers=[256, 128, 64], memory_size=1000000, batch_size=256):
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
        self.total_step_count = 0
        self.batch_size = batch_size

        self.cities = self.game.get_cities()

        num_cities = len(self.cities)
        self.action_functions = {self.build: {'name': 'build', 'use_colour': False},
                                 self.cure: {'name': 'cure', 'use_colour': True},
                                 self.give: {'name': 'give', 'use_colour': False},
                                 self.take: {'name': 'take', 'use_colour': False},
                                 self.treat: {'name': 'treat', 'use_colour': True}}
        self.actions = []
        self.fill_actions()
        self.num_actions = (3 * num_cities) + (2 * num_cities * len(DQNAgent.colours))
        self.memory = []
        self.memory_size = memory_size

        self.mask_action_values = mask_action_values

        self.target_net = None
        self.target_update_count = target_update_count
        self.using_target_net = target_network
        self.net = self.build_neural_net(initialise)
        self.net.summary()
        if self.using_target_net:
            self.target_net = self.build_neural_net(initialise)
            self.update_target_net()
        input("Run?")
        return

    def act(self, print_action=False, random_actions=False):
        # Chooses action
        action_index = self.choose_action(random_actions=random_actions)
        if action_index >= self.num_actions:
            print("Out of bounds index with " + str(action_index))
            input()
        action = self.actions[action_index]

        # Finds after state
        action_function = action[0]
        city_used = action[1]
        colour_used = action[2]
        if colour_used is None:
            after_state = action_function(city_used)
        else:
            after_state = action_function(city_used, colour_used)

        action_str = self.action_functions[action_function]['name']

        if print_action:
            to_print = action_str + " at " + city_used.get_name()
            if colour_used is not None:
                to_print += " with colour " + colour_used
            print(to_print)
        # Transitions to after state
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
        elif action_str == 'cure':
            if colour_used in after_state['cured_diseases']:
                self.game.cure_disease(colour_used)
        elif action_str == 'treat':
            new_cube_count = 0
            for i in range(1, 4):
                if city_used in after_state['infected_cities'][colour_used][i]:
                    new_cube_count = i
                    break
            city_used.set_cubes(colour_used, new_cube_count)
        return action_index

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
        net = keras.Sequential()
        init = tf.keras.initializers.HeUniform()
        if initialise:
            net.add(Dense(units=self.net_layers[0],
                               activation='relu',
                               input_dim=self.state_shape,
                               use_bias=False, kernel_initializer=init))
            for i in range(1, self.num_net_layers):
                net.add(Dense(units=self.net_layers[i],
                                   activation='relu',
                                   use_bias=False, kernel_initializer=init))
            net.add(Dense(units=self.num_actions, activation='linear'))
            net.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.alpha),
                             loss='mse',
                             metrics=['mse'])
        else:
            print("Cannot load data from file")
            return
            # Add load net from file
        return net

    def can_take_action(self, action_array, state=None):
        if state is None:
            state = self.current_state

        action = action_array[0]
        city_name = action_array[1].get_name()
        colour = action_array[2]

        action_player = self.players[self.current_turn]

        if action == self.build:  # Build: player needs city card in hand and no res station there
            for city in state['research_stations']:
                if city.has_name(city_name):
                    return False
            for card in state['city_cards']['player_hands'][self.current_turn]:
                if card.has_name(city_name):
                    return True
            return False
        if action == self.cure:  # Cure: player needs 5 or more colour of cards and res station at city
            has_station = False
            for city in state['research_stations']:
                if city.has_name(city_name):
                    has_station = True
                    break
            if not has_station:
                return False
            cards_needed = 5
            for card in state['city_cards']['player_hands'][self.current_turn]:
                if card.has_colour(colour):
                    cards_needed -= 1
            return cards_needed <= 0
        if action == self.give:  # give: player needs the city card in hand
            for card in state['city_cards']['player_hands'][self.current_turn]:
                if card.has_name(city_name):
                    return True
            return False
        if action == self.take:  # take: another player needs to be at the city with the card
            for i in range(self.player_count):
                if i == self.current_turn:
                    continue
                if state['player_locations'][i].has_name(city_name):
                    for card in state['city_cards']['player_hands'][i]:
                        if card.has_name(city_name):
                            return True
            return False
        if action == self.treat:  # treat: city needs to have colour cubes on it
            for cubes in range(1, 4):
                for city in state['infected_cities'][colour][cubes]:
                    if city.has_name(city_name):
                        return True
            return False
        return

    def choose_action(self, random_actions=False):
        if rand.uniform(0, 1) < self.epsilon or random_actions:  # Takes random action
            possible_actions = [action_index for action_index in range(self.num_actions - 1)
                                if self.can_take_action(self.actions[action_index])]
            return rand.choice(possible_actions)

        net_input = self.state_to_net_input(self.current_state)
        q_out = self.net(net_input.reshape(1, self.state_shape))

        # Masking q_values
        if self.mask_action_values:
            q_out = self.mask(q_out)

        max_value = q_out[0][0]
        possible_actions = [0]
        for i in range(1, self.num_actions):
            value = q_out[0][i]
            if value > max_value:
                max_value = value
                possible_actions = [i]
            elif value == max_value:
                possible_actions.append(i)

        action_index = rand.choice(possible_actions)
        result = q_out[0][action_index]
        if math.isinf(result) or math.isnan(result):
            print("Infinite result")
            input()
        if result == 0.0:
            print("Zero result")
            input()
        return action_index

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

    def fill_actions(self):
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
        return

    def find_move_after_state(self, current_node, action_points):
        after_state = copy_state(self.current_state)
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            card_used = current_node.get_used_card()
            if card_used is not None:
                after_state['city_cards']['player_hands'][self.current_turn].remove(card_used)
                after_state['city_cards']['discarded'].append(card_used)
            action_points -= 1
        after_state['player_locations'][self.current_turn] = current_node.get_city()
        return after_state, action_points

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

    def learn(self, terminal):
        if self.using_target_net:
            target_net = self.target_net
        else:
            target_net = self.net

        experience_sample = rand.sample(self.memory, self.batch_size)

        states = np.array([self.state_to_net_input(trajectory['state'])
                           for trajectory in experience_sample])
        next_states = np.array([self.state_to_net_input(trajectory['next_state'])
                                for trajectory in experience_sample])
        q_values_unmasked = target_net(next_states.reshape(self.batch_size, self.state_shape)).numpy()
        prediction_target_unmasked = target_net(states.reshape(self.batch_size, self.state_shape)).numpy()
        q_values = q_values_unmasked
        prediction_target = prediction_target_unmasked

        if self.mask_action_values:
            q_values = np.array([self.mask(q_values_unmasked[i], state=experience_sample[i]['next_state'])
                                 for i in range(self.batch_size)])
            prediction_target = np.array([self.mask(prediction_target_unmasked[i], state=experience_sample[i]['state'])
                                          for i in range(self.batch_size)])

        for i in range(self.batch_size):
            trajectory = experience_sample[i]
            action_index = trajectory['action']
            target = trajectory['reward']
            if not trajectory['terminal']:
                target += self.gamma * np.argmax(q_values[i][:])
            prediction_target[i][action_index] = target

        self.net.fit(states.reshape(self.batch_size, self.state_shape),
                     prediction_target, batch_size=self.batch_size)
        return

    def mask(self, values, state=None):
        mask_np = np.array([self.can_take_action(action, state=state) for action in self.actions])

        mask = tf.convert_to_tensor(mask_np, dtype=tf.bool)
        mask = tf.cast(mask, dtype=tf.float32)

        return values * mask

    def reset(self, new_game=None):
        self.current_state = {}
        self.turn_count = 0
        self.current_turn = 0
        if new_game is not None:
            self.game = new_game
            self.cities = self.game.get_cities()
            self.fill_actions()
        for player in self.players:
            player.reset_hand()
            player.move_to(self.game.get_city_by_name('Atlanta'))
        return

    def save_trajectory(self, trajectory):
        self.memory.append(trajectory)
        if len(self.memory) > self.memory_size:
            del (self.memory[0])
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

    def transition_and_learn(self, action_index, terminal, learn):
        # Transition to next state
        last_state = copy_state(self.current_state)
        self.set_current_state()
        self.current_turn = (self.current_turn + 1) % self.player_count
        self.turn_count += 1
        self.total_step_count += 1

        # Finding reward
        reward = reward_function(last_state, self.current_state, terminal)

        # save trajectory to memory
        trajectory = {'state': last_state,
                      'action': action_index,
                      'reward': reward,
                      'next_state': self.current_state,
                      'terminal': terminal}
        self.save_trajectory(trajectory)

        # Learn
        if learn:
            self.learn(terminal)
            # Updating target network
            if self.total_step_count % self.target_update_count == 0:
                self.update_target_net()
        return reward

    def treat(self, city, colour):
        acting_player = self.players[self.current_turn]

        # Finding path to city
        start_node = self.game.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Working out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        num_cubes = 0
        for i in range(1, 4):
            if city in self.current_state['infected_cities'][colour][i]:
                num_cubes = i
                break
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

    def update_target_net(self):
        self.target_net.set_weights(self.net.get_weights())
        print("Updating target net")
        return
