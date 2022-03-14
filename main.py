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

num_runs = 1
initialise = True

for i in range(num_runs):
    # Creating Game
    game = Game(window, 'qlearning', None, use_graphics, auto_run, print_results)

    # Creating or resetting agent
    if i <= 0:
        # Creating Agent
        agent = TDLambda(game, 2, window, game.get_city_by_name("Atlanta"), initialise)
    else:
        agent.q_learner_reset(game, window, game.get_city_by_name("Atlanta"))

    game.add_player(agent)

    game.setup_game()

    if use_graphics:
        game.draw_game()

    # Running Game
    game.run_game()

game.graph_results()

