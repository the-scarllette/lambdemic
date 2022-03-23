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

num_runs = 1000

lamb = 0.5
alpha = 0.001
gamma = 0.5
epsilon = 0.15
net_layers = 5

initialise = True
print_states = False

num_agents = 3


for k in range(num_agents):
    for i in range(num_runs):
        print("Run " + str(i))

        game = Game(window, 'TDLambda', None, use_graphics, auto_run, print_results)

        if i == 0:
            # Creating Agent
            agent = TDLambda(game, alpha, lamb, gamma, net_layers, 2, window, game.get_city_by_name("Atlanta"), epsilon)
        else:
            agent.reset(game)
        game.add_player(agent)

        # Setting up game
        game.setup_game()

        if use_graphics:
            game.draw_game()

        # Running Game
        game.train_td_lambda(print_states, k)
    game.graph_results(k)

game.average_graph(num_agents)


