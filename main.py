from game import Game
from graphics import *

window = GraphWin("Pandemicai", 1000, 500)

game = Game(window)
game.draw_game()

game.run_game()