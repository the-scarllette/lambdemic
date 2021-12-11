from player import Player

class LearningAgent(Player):

    player_colours = ["Orange", "Green", "Purple", "Brown"]

    def __init__(self, results_filename, learning_filename, player_count, window, start_city):
        self.__results_filename = results_filename
        self.__learning_file = learning_filename
        self.__players = []
        self.__player_count = player_count
        for i in range(self.__player_count):
            self.__players.append(Player("Player " + str(i), window, start_city, LearningAgent.player_colours[i], i*5))
        self.__current_turn = 0
        return

    def act(self):
        return 0

    def add_to_hand(self, card):
        self.__players[self.__current_turn].add_to_hand(card)
        return

    def draw(self):
        self.__players[self.__player_count].draw()
        return

    def get_results_filename(self):
        return self.__results_filename

    def initial_hands(self, cards_to_add):
        for i in range(len(cards_to_add)):
            self.__players[i % self.__player_count].add_to_hand(cards_to_add[i])
        return