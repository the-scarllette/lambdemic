from game import Game
from graphics import *

width = 1000
hight = 600

window = GraphWin("Pandemicai", width, hight)

game = Game(window, 'random', True, False)
game.draw_game()

game.run_game()