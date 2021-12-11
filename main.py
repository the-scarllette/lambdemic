from game import Game
from graphics import *
from pathnode import PathNode
from citycard import CityCard

width = 1000
hight = 600

use_graphics = False

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, hight)

agent = None

game = Game(window, 'random', agent, use_graphics, True, True)

if use_graphics:
    game.draw_game()

game.run_game()


