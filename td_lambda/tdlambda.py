from neuralnet.neuralnet import NeuralNet
from learningagent import LearningAgent
from numpy import random
from game import Game
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import math

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


class TDLambda(LearningAgent):
    learning_file = 'td_lambda/tdlambda_learning_data.json'
    results_file = 'results/tdlambda_results.json'

    cure_reward = 10  # Reward for curing a disease
    lose_game_reward = -10
    
    def __init__(self, game, alpha, lamb, gamma, net_layers, player_count, window, start_city, epsilon=0.0):
        super(TDLambda, self).__init__(game, TDLambda.learning_file, TDLambda.results_file,
                                       player_count, window, start_city)
        self.actions = {self.give: 'give',
                        self.treat: 'treat',
                        self.build: 'build',
                        self.take: 'take',
                        self.cure: 'cure'}
        self.alpha = alpha
        self.lamb = lamb
        self.epsilon = epsilon
        self.gamma = gamma
        self.net_layers = net_layers
        self.num_net_inputs = 726 + (96*self.player_count)
        self.net = None
        self.build_neural_net()
        self.current_state = {}
        self.cities = self.game.get_cities()
        self.state_history = []
        self.reward_history = []
        self.turn_count = 0
        self.gradient_tape = None
        return
    
    def act(self, print_action=False):
        # Chooses action
        action, after_state, params = self.choose_action()

        # Finding out what action chosen
        action_str = self.actions[action]

        # Printing Action
        print(action_str + " at " + params[0].get_name())

        # Taking action
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
            res_station_city = params[0]
            res_station_city.set_has_res_station(True)
            return
        if action_str == 'cure':
            self.game.cure_disease(params[1])
            return
        if action_str == 'treat':
            used_city = params[0]
            used_colour = params[1]
            new_cube_count = 0
            for i in range(1, 4):
                if used_city in after_state['infected_cities'][used_colour][i]:
                    new_cube_count = i
                    break
            used_city.set_cubes(used_colour, new_cube_count)
            return
        return
    
    def build_neural_net(self):
        self.net = keras.Sequential()
        init = tf.keras.initializers.HeUniform()
        for i in range(self.net_layers - 2):
            self.net.add(keras.layers.Dense(input_shape=(self.num_net_inputs, ), units=self.num_net_inputs,
                                            activation='relu', use_bias=False, kernel_initializer=init))
        self.net.add(keras.layers.Dense(input_shape=(self.num_net_inputs,), units=1, use_bias=False))
        self.net.compile(loss=tf.keras.losses.Huber(),
                         optimizer=tf.keras.optimizers.Adam(learning_rate=self.alpha),
                         metrics=['accuracy'])
        self.net.summary()
        return
    
    def choose_action(self):
        possible_actions = []
        acting_player = self.players[self.current_turn]

        # Getting all possible actions and their after_states
        for action in self.actions:
            if self.actions[action] == 'build' and len(self.game.get_research_stations()) >= 6:
                continue
            for city in self.cities:
                takes_colour_input = True
                for colour in Game.colours:
                    if self.actions[action] == 'cure' and not acting_player.can_cure(colour):
                        continue
                    if not takes_colour_input:
                        break
                    try:
                        after_state = action(acting_player, city, colour)
                        params = [city, colour]
                    except TypeError:
                        after_state = action(acting_player, city)
                        params = [city]
                        takes_colour_input = False
                    if after_state is not None:
                        possible_actions.append({'action': action,
                                                 'after_state': copy_state(after_state),
                                                 'params': params})

        # Choosing which action to take
        if random.uniform(0, 1) <= self.epsilon:  # Takes random action
            choice = random.choice(possible_actions)
            return choice['action'], choice['after_state'], choice['params']
        # Find best action and takes it
        max_value = self.compute_state_value(possible_actions[0]['after_state'])
        best_action_indexes = [0]
        for i in range(1, len(possible_actions)):
            possible_action = possible_actions[i]
            value = self.compute_state_value(possible_action['after_state'])
            if value > max_value:
                max_value = value
                best_action_indexes = [i]
            elif value == max_value:
                best_action_indexes.append(i)
        choice = possible_actions[random.choice(best_action_indexes)]
        return choice['action'], choice['after_state'], choice['params']

    def compute_state_value(self, state):
        # Converts state into inputs
        net_input = self.state_to_net_input(state)

        # Runs state through neural net
        result = self.net(net_input)
        result = float(result[0][0])
        if math.isnan(result) or math.isinf(result):
            print("HERE")
            input()
        return result
    
    def lambda_return(self, i):
        for k in range(0, self.turn_count):
            state = self.state_history[k]
            with tf.GradientTape() as self.gradient_tape:
                net_result = self.net(self.state_to_net_input(state))
            gradient = self.gradient_tape.gradient(net_result, self.net.weights)
            gradient = gradient[i]
            modifier = self.lamb ** (self.turn_count - k)
            gradient = modifier * gradient
            if k <= 0:
                lam_return = gradient
            else:
                lam_return += gradient
        return lam_return
    
    def load_neural_net(self):
        self.net = NeuralNet(net_filename=TDLambda.learning_file)
        return

    def reset(self, new_game=None):
        self.current_state = {}
        self.state_history = []
        self.reward_history = []
        self.turn_count = 0
        if new_game is not None:
            self.game = new_game
            self.cities = self.game.get_cities()
        self.update_state()
        for player in self.players:
            player.reset_hand()
            player.move_to(self.game.get_city_by_name('Atlanta'))
        return

    def save_agent(self):
        self.net.save_net(TDLambda.learning_file)
        return
    
    def update_neural_net(self, is_terminal):
        # Sees state change and updates state_history
        last_state = copy_state(self.current_state)
        self.state_history.append(last_state)
        self.update_state()
        self.turn_count += 1

        # Observes reward
        # 1 for each turn
        reward = 1
        last_cured = self.state_history[-1]['cured_diseases']
        for colour in self.current_state['cured_diseases']:
            reward += TDLambda.cure_reward
        if is_terminal and len(self.current_state['cured_diseases']) < 4:
            reward += TDLambda.lose_game_reward
        self.reward_history.append(reward)
        print("Reward: " + str(reward))
        
        # Updates neural net, terminal states are always 0 so just compares rewards
        temporal_diff = reward - self.compute_state_value(last_state)
        if not is_terminal:
            temporal_diff += self.gamma * self.compute_state_value(self.current_state)

        for k in range(0, self.turn_count):
            state = self.state_history[k]
            with tf.GradientTape() as g:
                net_result = self.net(self.state_to_net_input(state))
            gradient = g.gradient(net_result, self.net.weights)
            modifier = self.lamb ** (self.turn_count - k - 1)
            update_amounts = [tf.math.scalar_mul(modifier, gradient[grad]) for grad in range(self.net_layers - 1)]
            if k <= 0:
                lam_return = update_amounts
            else:
                lam_return = [tf.math.add(update_amounts[j], lam_return[j]) for j in range(self.net_layers - 1)]
        for i in range(self.net_layers - 1):
            layer = self.net.get_layer(index=i)
            weights = layer.get_weights()
            to_add = tf.math.scalar_mul(self.alpha * temporal_diff, lam_return[i])
            new_weights = tf.math.add(weights, to_add)
            layer.set_weights(new_weights)
        
        # Changes current turn
        self.current_turn = (self.current_turn + 1) % self.player_count
        
        # Returns reward
        return reward
