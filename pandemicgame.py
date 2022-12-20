from city import City

import json

# TODO: Add roles
# TODO: Change actions to primitive ones
# TODO: Change step function to account for card holding


class PandemicGame:
    starting_cities = {'blue': 'Atlanta',
                       'yellow': 'Lagos',
                       'black': 'Moscow',
                       'red': 'Sydney'}

    all_colours = ['blue', 'yellow', 'black', 'red']

    game_data_path = 'game_data.json'

    infection_rate_track = [2, 2, 2, 3, 3, 4, 4]

    def __init__(self, colours=all_colours,
                 player_count=2, num_epidemics=4):

        self.cubes = None
        self.colours = colours
        self.cities = []
        self.cured = {colour: False for colour in self.colours}
        self.current_turn = 0
        self.epidemics_drawn = 0
        self.num_colours - len(self.colours)
        self.player_count = player_count
        self.player_deck = None
        self.infection_deck = None
        self.research_stations = None
        self.terminal = True

        # Creating Game board
        with open(PandemicGame.game_data_path) as f:
            self.game_data = json.load(f)
            self.num_cites = sum([len(self.game_data[colour]) for colour in self.colours])
        self.city_names = {colour: [city_name for city_name in self.game_data[colour]]
                           for colour in self.colours}

        # NUM_CITIES = C, NUM_COLOURS = D, PLAYER_COUNT = P
        # C(3D + 2P + 1 + 1 + 1) + D + P + 2
        # EACH CITY:
        #   ECH COLOUR: 1 CUBE, 2 CUBE, 3 CUBE
        #   EACH PLAYER: IN CITY, CARD IN HAND
        #   Has research station
        #   City card in discard pile
        #   Infection card in discard pile
        # Each colour: Is cured
        # Each player: current turn
        self.state_shape = (self.num_cites * ((3 * self.num_colours) + (2 * self.player_count) + 3) +
                            self.num_colours + self.player_count)

        return


def reset(self):
    self.cities = [City(city_name, colour) for colour in self.colours
                   for city_name in self.game_data[colour]]
    return
