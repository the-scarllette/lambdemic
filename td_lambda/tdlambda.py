import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from tensorflow import keras
from keras.layers import Dense
from keras import backend
import tensorflow as tf
import random as rand

'''
Optimal values:
blue: [64, 32, 16], alpha=10^-5, lamb=0.5, batch_size=4
'''


class TDLambdaAgent:

    def __init__(self, state_shape, action_shape, initialise=True,
                 alpha=0.0000001, lamb=0.5, epsilon=0.1,
                 net_layers=[64, 32, 16, 16], memory_sze=10000000,
                 experience_replay=False, batch_size=2,
                 use_target_network=False, target_network_step=5,
                 check_point_name=None, checkpoint_step=2000):
        self.num_episodes = 0

        self.alpha = alpha
        self.lamb = lamb
        self.epsilon = epsilon
        self.net_layers = net_layers
        self.num_net_layers = len(self.net_layers)

        self.action_state = action_shape
        self.state_shape = state_shape
        self.batch_size = batch_size

        self.current_episode = []
        self.memory = []
        self.memory_size = memory_sze

        self.experience_replay = experience_replay

        self.checkpoint_path = check_point_name
        self.net = self.build_neural_net(initialise)
        self.net.summary()
        self.use_target_net = use_target_network
        if self.use_target_net:
            self.target_net = self.build_neural_net(initialise)
            self.update_target_net()
            self.target_network_step = target_network_step

        self.checkpoint_step = checkpoint_step
        if self.checkpoint_path is not None:
            self.checkpoint_dir = os.path.dirname(self.checkpoint_path)
            self.cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=self.checkpoint_path,
                                                                  save_weights_only=True,
                                                                  verbose=1)
        return

    def build_neural_net(self, initialise):
        net = keras.Sequential()
        init = tf.keras.initializers.HeUniform()
        net.add(Dense(units=self.net_layers[0],
                      activation='relu',
                      input_dim=self.state_shape,
                      use_bias=False,
                      kernel_initializer=init))
        for i in range(1, self.num_net_layers):
            net.add(Dense(units=self.net_layers[i],
                          activation='relu',
                          use_bias=False,
                          kernel_initializer=init))
        net.add(Dense(units=1, activation='linear'))
        net.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.alpha),
                    loss='mse',
                    metrics=['mse'])
        if not initialise:
            net.load_weights(self.checkpoint_path)
        return net

    def choose_action(self, possible_actions, possible_after_states, random_action=False, print_values=False):
        # If can't take any action whatsoever takes a fully random action
        if len(possible_actions) <= 0:
            return rand.randint(0, self.action_state - 1)

        # Taking random action
        if random_action or rand.uniform(0, 1) <= self.epsilon:
            return rand.choice(possible_actions)

        # Finding highest after_state value
        max_after_state_value = self.net(possible_after_states[0].reshape(1, self.state_shape))[0][0]
        action_choices = [possible_actions[0]]
        if print_values:
            print("After state values")
            print("Action: " + str(action_choices[0]) + " value: " + str(max_after_state_value))
        for i in range(1, len(possible_actions)):
            value = self.net(possible_after_states[i].reshape(1, self.state_shape))[0][0]
            action = possible_actions[i]

            if print_values:
                print("Action: " + str(action) + " value: " + str(value))

            if value == max_after_state_value:
                action_choices.append(action)
            elif value > max_after_state_value:
                max_after_state_value = value
                action_choices = [action]
        return rand.choice(action_choices)

    def learn(self):
        if self.experience_replay:
            episodes = rand.sample(self.memory, self.batch_size)
        else:
            episodes = [self.current_episode]

        if self.use_target_net:
            target_net = self.target_net
        else:
            target_net = self.net

        for episode in episodes:
            num_steps = rand.randint(1, len(episode))

            last_trajectory = episode[num_steps - 1]
            target = last_trajectory['reward']
            if not last_trajectory['terminal']:
                target += target_net(last_trajectory['next_state'].reshape(1, self.state_shape))
            else:
                target = tf.convert_to_tensor([[target]])

            # TD(0) Update
            if self.num_episodes % self.checkpoint_step == 0 and last_trajectory['terminal']:
                self.net.fit(last_trajectory['state'].reshape(1, self.state_shape),
                             target.numpy(),
                             callbacks=[self.cp_callback])
            else:
                self.net.fit(last_trajectory['state'].reshape(1, self.state_shape),
                             target.numpy())

            # TD(Lambda) note: here's the good stuff baby
            if num_steps > 1:
                target = target - target_net(last_trajectory['state'].reshape(1, self.state_shape))
                current_learning_rate = self.alpha
                t = num_steps - 2
                while t >= 0:
                    current_learning_rate *= self.lamb
                    backend.set_value(self.net.optimizer.learning_rate, current_learning_rate)
                    current_state = episode[t]['state']
                    current_target = target + self.net(current_state.reshape(1, self.state_shape))

                    self.net.fit(current_state.reshape(1, self.state_shape), current_target)
                    t -= 1
                backend.set_value(self.net.optimizer.learning_rate, self.alpha)
        return

    def reset_for_next_episode(self):
        if len(self.current_episode) > 0:
            self.memory.append(self.current_episode.copy())
        self.current_episode = []
        self.num_episodes += 1

        if len(self.memory) > self.memory_size:
            del self.memory[rand.randint(0, self.memory_size)]

        if self.use_target_net and self.num_episodes % self.target_network_step == 0:
            self.update_target_net()
        return

    def save_trajectory(self, state, action, reward, next_state, terminal):
        trajectory = {'state': state,
                      'action': action,
                      'reward': reward,
                      'next_state': next_state,
                      'terminal': terminal}

        self.current_episode.append(trajectory)
        return

    def set_epsilon(self, new_value):
        self.epsilon = new_value
        return

    def update_target_net(self):
        self.target_net.set_weights(self.net.get_weights())
        print("Updated Target Net")
        return
