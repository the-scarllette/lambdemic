import random

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

    def discard_to_hand_limit(self):
        for player in self.players:
            hand = player.get_hand()
            while len(hand) > 7:
                to_discard = random.choice(hand)
                player.discard_card_by_name(to_discard.get_name())
                hand = player.get_hand()
        return

    def draw(self):
        for player in self.players:
            player.draw()
        return

    def get_results_filename(self):
        return self.results_filename

    def initial_hands(self, cards_to_add):
        for i in range(len(cards_to_add)):
            self.players[i % self.player_count].add_to_hand(cards_to_add[i])
        return

    def observe_reward(self):
        return 0

    def reset_game(self, new_game, new_window, new_start_city):
        self.game = new_game
        self.window = new_window
        self.players = []
        for i in range(self.player_count):
            self.players.append(Player("Player " + str(i), self.window, new_start_city,
                                       LearningAgent.player_colours[i], i*5))
        self.current_turn = 0
        return
