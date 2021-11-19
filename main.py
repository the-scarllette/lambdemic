from game import Game
from graphics import *
from pathnode import PathNode
from citycard import CityCard

width = 1000
hight = 600

use_graphics = True

window = None
if use_graphics:
    window = GraphWin("Pandemicai", width, hight)

agent = None

game = Game(window, 'random', agent, use_graphics, True, True)

if use_graphics:
    game.draw_game()

#game.run_game()

while True:
    start_city = game.find_city_by_name(input("Where to start"))
    end_city = game.find_city_by_name(input("where to end"))
    current_node = game.find_path(start_city, end_city, [CityCard(game.find_city_by_name("Atlanta")), CityCard(game.find_city_by_name("Jakarta"))])

    print("Path is:")
    finished_path = False
    cost = 0
    while True:
        action = current_node.get_next_action()
        if action is None:
            break
        print(action + " to get to " + current_node.get_next_node().get_name())
        current_node = current_node.get_next_node()
    print("actions = " + str(current_node.get_cost()))

