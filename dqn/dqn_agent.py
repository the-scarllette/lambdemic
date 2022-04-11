import math

import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from learningagent import LearningAgent
from game import Game
import random as rand
import numpy as np

''' State details:
Current players turn

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
other inputs: 1 + 1 + 1 + 4
total: 727 + 96*player_count

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


class DQNAgent:
    learning_file = 'dqn/dqn_learning_data.json'
    results_file = 'results/dqn_results.json'

    def __init__(self, state_shape, action_shape, initialise=True, target_network=False, target_update_count=32,
                 mask_action_values=True,
                 alpha=0.001, gamma=0.9, epsilon=0.2,
                 net_layers=[32, 16], memory_size=1000000, batch_size=32):

        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.net_layers = net_layers
        self.num_net_layers = len(self.net_layers)
        self.action_shape = action_shape
        self.state_shape = state_shape
        self.total_step_count = 0
        self.batch_size = batch_size

        self.actions = []
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
        input("run?")
        return

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
            net.add(Dense(units=self.action_shape, activation='linear'))
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

    def choose_action(self, state, random_actions=False):
        if rand.uniform(0, 1) < self.epsilon or random_actions:  # Takes random action
            return rand.randint(0, self.action_shape - 1)

        q_out = self.net(state.reshape(1, self.state_shape))

        # Masking q_values
        if self.mask_action_values:
            q_out = self.mask(q_out)

        max_value = q_out[0][0]
        possible_actions = [0]
        for i in range(1, self.action_shape):
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

    def learn(self):
        if self.using_target_net:
            target_net = self.target_net
        else:
            target_net = self.net

        experience_sample = rand.sample(self.memory, self.batch_size)

        states = np.array([trajectory['state']
                           for trajectory in experience_sample])
        next_states = np.array([trajectory['next_state']
                                for trajectory in experience_sample])
        q_values = target_net(next_states.reshape(self.batch_size, self.state_shape)).numpy()
        prediction_target = target_net(states.reshape(self.batch_size, self.state_shape)).numpy()

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

    def mask(self, values, mask=None, state=None):
        if mask is None:
            return values
        # TODO: Change masking function
        mask_np = np.array([self.can_take_action(action, state=state) for action in self.actions])

        mask = tf.convert_to_tensor(mask_np, dtype=tf.bool)
        mask = tf.cast(mask, dtype=tf.float32)

        return values * mask

    def save_trajectory(self, state, action, reward, next_state, terminal):
        trajectory = {'state': state,
                      'action': action,
                      'reward': reward,
                      'next_state': next_state,
                      'terminal': terminal}

        self.memory.append(trajectory)
        if len(self.memory) > self.memory_size:
            del (self.memory[0])
        return
