from game import Game
from graphics import *
from dqn.dqn_agent import DQNAgent
from results.resultsmanager import ResultsManager
from neuralnet.neuralnet import NeuralNet

# Initialising Window
width = 1000
height = 600
use_graphics = False
auto_run = True
print_results = False

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, height)

random_episodes = 100
num_episodes = 400 + random_episodes

lamb = 0.5
alpha = 0.001
gamma = 0.5
epsilon = 0.15
net_layers = 5

initialise = True
print_states = False

num_agents = 3


for k in range(num_agents):
    for episode in range(num_episodes):
        print("Run " + str(episode))
        learn = episode > random_episodes

        game = Game(window, 'DQN', None, use_graphics, auto_run, print_results)

        if episode == 0:
            # Creating Agent
            agent = DQNAgent(game, window, game.get_city_by_name('Atlanta'))
        else:
            agent.reset(game)
        game.add_player(agent)

        # Setting up game
        game.setup_game()

        if use_graphics:
            game.draw_game()

        # Running Game
        game.train_agent(print_states, agent_num=None, learn=learn)

# TODO: agent runs random actions
# TODO: agent chooses action
#
