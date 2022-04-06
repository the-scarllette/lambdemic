from game import Game
from graphics import *
from dqn.dqn_agent import DQNAgent
from graphing import graph_local_average

# Initialising Window
width = 1000
height = 600
use_graphics = False
auto_run = True
print_results = False

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, height)

random_episodes = 500
training_episodes = 1000
num_episodes = training_episodes + random_episodes

alpha = 0.0000000001
gamma = 0.99
epsilon = 0.1

initialise = True
print_states = False
print_actions = True
print_reward = True

use_target_network = True
target_update_count = 100

num_agents = 1

for k in range(num_agents):
    total_rewards = []
    for episode in range(num_episodes):
        print("Run " + str(episode))
        learn = episode > random_episodes

        game = Game(window, 'DQN', None, use_graphics, auto_run, print_results)

        if episode == 0:
            # Creating Agent
            agent = DQNAgent(game, window, game.get_city_by_name('Atlanta'),
                             alpha=alpha, gamma=gamma, epsilon=epsilon, initialise=initialise,
                             target_network=use_target_network, target_update_count=target_update_count)
        else:
            agent.reset(game)
        game.add_player(agent)

        # Setting up game
        game.setup_game()

        if use_graphics:
            game.draw_game()

        # Running Game
        total_reward = game.train_agent(print_states, print_actions=print_actions, agent_num=None, learn=learn)
        if learn:
            total_rewards.append(total_reward)
        if print_reward:
            print("Total Reward: " + str(total_reward))
    graph_local_average(total_rewards, c=training_episodes // 100)

