import math

import tensorflow as tf
from tensorflow import keras
from keras import layers
from learningagent import LearningAgent
import random as rand
import numpy as np


class DQNAgent:

    def __init__(self, actions, state_shape, alpha=0.001, gamma=0.9, epsilon=0.15, model_layers=[64], batch_size=32,
                 memory_size=10000):
        self.actions = actions
        self.state_shape = state_shape
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.model_layers = model_layers
        self.num_layers = len(self.model_layers)
        self.batch_size = batch_size

        self.memory_size = memory_size
        self.experience = []

        self.q_net = None
        self.build_q_net()
        return

    def build_q_net(self):
        self.q_net = keras.Sequential()
        self.q_net.add(layers.Dense(units=self.model_layers[0],
                                    activation='relu',
                                    input_dim=self.state_shape))
        for i in range(1, self.num_layers):
            self.q_net.add(layers.Dense(units=self.model_layers[i],
                                        activation='relu'))
        self.q_net.add(layers.Dense(units=self.actions, activation='linear'))
        self.q_net.compile(optimizer=tf.keras.optimizers.Adam(lr=self.alpha),
                           loss='mse',
                           metrics=['mae', 'mse'])
        self.q_net.summary()
        return

    def choose_action(self, state, possible_actions=[]):
        if not possible_actions:
            possible_actions = list(range(self.actions))

        if rand.uniform(0, 1) <= self.epsilon:  # Chooses random action
            return rand.choice([i for i in possible_actions])

        q_out = self.q_net(np.array(state).reshape(1, self.state_shape))
        best_value = -np.inf
        chosen_actions = []
        for i in possible_actions:
            value = q_out[i]
            if value == best_value:
                chosen_actions.append(i)
            elif value > best_value:
                best_value = value
                chosen_actions = [i]

        action = rand.choice(chosen_actions)
        return action

    def learn(self):
        experience_sample = rand.sample(self.experience, self.batch_size)

        states = np.array([trajectory['state'] for trajectory in experience_sample])
        next_states = np.array([trajectory['next_state'] for trajectory in experience_sample])
        q_values = self.q_net.predict(next_states.reshape(self.batch_size, self.state_shape))
        prediction_target = self.q_net(states.reshape(self.batch_size, self.state_shape)).numpy()

        for i in range(self.batch_size):
            trajectory = experience_sample[i]
            action = trajectory['action']
            target = trajectory['reward']
            if not trajectory['terminal']:
                target += self.gamma * np.amax(q_values[i][:])
            prediction_target[i][action] = target

        self.q_net.fit(states.reshape(self.batch_size, self.state_shape),
                       prediction_target, batch_size=self.batch_size)
        return

    def save_trajectory(self, current_state, action, reward, next_state, terminal):
        to_save = {'state': current_state,
                   'action': action,
                   'reward': reward,
                   'next_state': next_state,
                   'terminal': terminal}
        self.experience.append(to_save)
        if len(self.experience) > self.memory_size:
            del(self.experience[0])
        return

