from game import Game
from graphics import *
from pathnode import PathNode
from citycard import CityCard
from qlearning.qlearningagent import QLearningAgent
from results.resultsmanager import ResultsManager

width = 1000
hight = 600

use_graphics = False

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, hight)

agent = None

game = Game(window, 'random', agent, use_graphics, True, True)

agent = QLearningAgent(game, 2, window, game.get_city_by_name("Atlanta"))

agent.initialise_q_values()

if use_graphics:
    game.draw_game()

#game.run_game()

