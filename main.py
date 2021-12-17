from game import Game
from graphics import *
from qlearning.qlearningagent import QLearningAgent

# Initalising Window
width = 1000
height = 600
use_graphics = False

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, height)

num_runs = 2000
initialise = False

for i in range(0):
    # Creating Game
    game = Game(window, 'qlearning', None, use_graphics, True, True)

    # Creating Agent
    agent = QLearningAgent(game, 2, window, game.get_city_by_name("Atlanta"), initialise)
    game.add_player(agent)

    game.setup_game()

    if use_graphics:
        game.draw_game()

    # Running Game
    game.run_game()

game = Game(window, 'qlearning', None, use_graphics, True, True)
agent = QLearningAgent(game, 2, window, game.get_city_by_name("Atlanta"), initialise)
game.add_player(agent)

game.setup_game()
#game.graph_results()

game.print_cured_data()
