from game import Game
from graphics import *
from qlearning.qlearningagent import QLearningAgent
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

num_runs = 40000
initialise = True

for i in range(num_runs):
    teach_agent = ((i % 1000 == 0) and i > 0) or (i == num_runs - 1)

    # Creating Game
    game = Game(window, 'qlearning', None, use_graphics, auto_run, print_results, teach_agent)

    # Creating or resetting agent
    if i <= 0:
        # Creating Agent
        agent = QLearningAgent(game, 2, window, game.get_city_by_name("Atlanta"), initialise)
    else:
        agent.q_learner_reset(game, window, game.get_city_by_name("Atlanta"))

    game.add_player(agent)

    game.setup_game()

    if use_graphics:
        game.draw_game()

    # Running Game
    game.run_game()

game.graph_results()

