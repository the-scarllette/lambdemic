from player import Player

class LearningAgent(Player):

    player_colours = ["Orange", "Green", "Purple", "Brown"]

    def __init__(self, game, learning_filename, results_filename, player_count, window, start_city):
        self.game = game
        self.results_filename = results_filename
        self.learning_file = learning_filename
        self.players = []
        self.player_count = player_count
        for i in range(self.player_count):
            self.players.append(Player("Player " + str(i), window, start_city, LearningAgent.player_colours[i], i*5))
        self.current_turn = 0
        return

    def act(self):
        return 0

    def add_to_hand(self, card):
        self.players[self.current_turn].add_to_hand(card)
        return

    def draw(self):
        self.players[self.player_count].draw()
        return

    def get_results_filename(self):
        return self.results_filename

    def initial_hands(self, cards_to_add):
        for i in range(len(cards_to_add)):
            self.players[i % self.player_count].add_to_hand(cards_to_add[i])
        return