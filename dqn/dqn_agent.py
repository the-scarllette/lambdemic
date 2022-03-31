import tensorflow as tf
from tensorflow import keras
from keras.layers import Dense
from player import Player
from game import Game

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


class DQNAgent(Player):
    learning_file = 'dqn/dqn_learning_data.json'
    results_file = 'results/dqn_results.json'

    colours = Game.colours

    def __init__(self, game, window, start_city, initialise=True, player_count=2,
                 alpha=0.0001, gamma=0.9, epsilon=0.1,
                 net_layers=[64], memory_size=10000, batch_size=32):
        super(DQNAgent, self).__init__(game, DQNAgent.learning_file, DQNAgent.results_file,
                                       player_count, window, start_city)
        self.actions = {self.give: 'build',
                        self.treat: 'cure',
                        self.build: 'give',
                        self.take: 'take',
                        self.cure: 'treat'}

        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.net_layers = net_layers
        self.num_net_layers = len(self.net_layers)
        self.state_shape = 726 + (96 * self.player_count)
        self.net = None
        self.build_neural_net(initialise)
        self.current_state = {}
        self.turn_count = 0
        self.batch_size = batch_size

        self.cities = self.game.get_cities()

        num_cities = len(self.cities)
        self.num_actions = (3 * num_cities) + (2 * num_cities * len(DQNAgent.colours))
        self.memory = []
        self.memory_size = memory_size
        return

    # TODO: add action functions

    # Add act
    def act(self):
        return

    def build_neural_net(self, initialise):
        self.net = keras.Sequential()
        if initialise:
            self.q_net.add(Dense(units=self.model_layers[0],
                                 activation='relu',
                                 input_dim=self.state_shape))
            for i in range(1, self.num_net_layers):
                self.q_net.add(Dense(units=self.model_layers[i],
                                     activation='relu'))
            self.q_net.add(Dense(units=self.num_actions, activation='linear'))
            self.q_net.compile(optimizer=tf.keras.optimizers.Adam(lr=self.alpha),
                               loss='mse',
                               metrics=['mae', 'mse'])
        else:
            print("Cannot load data from file")
            return
            # TODO: add load net from file
        self.net.summary()
        return

    # Add learn
    def learn(self, terminal):
        return

    # TODO: build agent reset
    def reset(self):
        return

    # Add saving trajectory
    def save_trajectory(self, terminal):
        return

    # Add transitioning to next state
    def transition(self, terminal):
        return
