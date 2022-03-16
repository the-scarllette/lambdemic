from game import Game
from graphics import *
from td_lambda.tdlambda import TDLambda
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

num_runs = 100

lamb = 0.9
alpha = 0.5
epsilon = 0.1
net_layers = 3

initialise = True
print_states = False

for i in range(num_runs):
    print("Run " + str(i))
    if initialise:
        initialise = i == 0

    # Creating Game
    game = Game(window, 'qlearning', None, use_graphics, auto_run, print_results)

    # Creating Agent
    agent = TDLambda(game, alpha, lamb, net_layers, 2, window, game.get_city_by_name("Atlanta"), initialise, epsilon)

    game.add_player(agent)

    game.setup_game()

    if use_graphics:
        game.draw_game()

    # Running Game
    game.train_td_lambda(print_states)
    agent.save_agent()

game.graph_results()

