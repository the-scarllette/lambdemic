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

num_runs = 20


for i in range(num_runs):
    # Creating Game
    game = Game(window, 'qlearning', None, use_graphics, True, True)

    # Creating Agent
    initialise = False
    if i == 0:
        initialise = True
    agent = QLearningAgent(game, 2, window, game.get_city_by_name("Atlanta"), initialise)
    game.add_player(agent)

    game.setup_game()

    if use_graphics:
        game.draw_game()

    # Running Game
    game.run_game()
