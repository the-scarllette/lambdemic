from learningagent import LearningAgent
from game import Game
from generalfunctions import *
import random
import json

'''
    Data stored on environment:
        How many cubes on board
        How many cards of each colour needed to cure a disease
        Research Station on board
        Cured diseases

    Rewards:
        -For loosing game
        +For each cure
        +For game win

    States encoded as:
        {Number of cubes on the board}
        {Cards_to_cureBlue}{Cards_to_cureYellow}{Cards_to_cureBlack}{Cards_to_cureRed}
        {Research_stations_on_board}
        {0/1CureBlue}{0/1CureYellow}{0/1CureBlack}{01/CuredRed}

    Possible Actions:
        treat
            Moves to closest city with disease cubes
            Removes as many cubes as possible
        build
            Moves to closest card location
            Builds research station there if there isn't already one
        give
            Out of the cards in hand and other players,
            moves to the city that it has a card of and is closets to another player
            If it can, then gives the card
        take
            If player has card of the city they are in
            Moves to the closest player that matches this cretieria
            Takes card
        cure
            If have enough cards to cure an uncured disease
            moves to research station and cures

    State-action space size:
        (theoretical maximum) )states: 96 x 5^4 x 5 x 2^4 = 4,800,000
        actions: 5
        state action space : 24,000,000
'''


class QLearningAgent2(LearningAgent):
    results_file = 'results/qlearning2_results.json'
    learning_file = 'qlearning/learning_data2.json'

    possible_actions_str = ["treat", "build", "give", "take", "cure"]

    # Learning Rate
    alpha = 0.8

    # Epsilon in epsilon-greedy function
    epsilon = 0.2

    # Discounting Factor
    gamma = 0.9

    def __init__(self, game, player_count, window, start_city, initialise):
        super(QLearningAgent2, self).__init__(game, QLearningAgent2.learning_file, QLearningAgent2.results_file,
                                              player_count, window, start_city)

        if initialise:
            self.initialise_q_values()
        with open(self.learning_file) as json_file:
            self.q_values = json.load(json_file)

        self.current_state = self.get_state_code()
        self.possible_actions = {"treat": self.treat,
                                 "build": self.build,
                                 "give": self.give,
                                 "take": self.take,
                                 "cure": self.cure}
        self.last_action = None
        return

    def act(self):
        action_taken = False
        unavailable_actions = []

        # Using epsilon-greedy to determine if to take a random action
        random_action = False
        x = random.randint(1, 100)
        if x <= self.epsilon * 100:  # Take a random action
            random_action = True
        # If not takes action that maximises reward

        while not action_taken:
            if random_action:
                action = random.choice(self.possible_actions_str)
            else:
                action = self.choose_optimal_action(self.current_state, unavailable_actions)

            unavailable_actions.append(action)

            # Takes action
            action_taken = self.possible_actions[action](self.players[self.current_turn])
            self.last_action = action

        print("Player " + self.players[self.current_turn].get_name() + " took action " + self.last_action)
        self.current_turn = (self.current_turn + 1) % self.player_count
        return

    def build(self, acting_player):
        # Checks if 6 research stations are on board, if there are does not build
        if len(self.game.get_research_stations()) >= 6:
            return False

        # Finds the closest city based on cards in hand
        hand = acting_player.get_hand().copy()
        path_node = None
        min_path_cost = 1000

        for card in hand:
            if card.get_city().has_research_station():
                continue

            hand.remove(card)

            start_node = self.game.find_path(acting_player.get_city(), card.get_city(), hand)
            cost = start_node.get_total_cost()
            if cost < min_path_cost:
                path_node = start_node
                min_path_cost = cost

            hand.append(card)

        if path_node is None:
            return False

        remaining_action_points = self.move_player(acting_player, path_node, 4)

        if remaining_action_points <= 0:
            return True

        current_city = acting_player.get_city()
        acting_player.discard_card_by_name(current_city.get_name())
        current_city.set_has_res_station(True)
        return True

    def choose_optimal_action(self, current_state, unavailable_actions):
        best_action = QLearningAgent2.possible_actions_str[0]
        best_q_value = -1000000

        for action_value in self.q_values[current_state]:
            if action_value["value"] > best_q_value and action_value["action"] not in unavailable_actions:
                best_action = action_value["action"]
                best_q_value = action_value["value"]

        return best_action

    def cure(self, acting_player):
        # Checks if can cure disease and disease is not cured
        colour_to_cure = None
        hand = acting_player.get_hand().copy()
        for colour in Game.colours:
            count = 0
            for card in hand:
                if card.get_colour() == colour:
                    count += 1
            if count >= 5 and not self.game.is_cured(colour):
                colour_to_cure = colour
                break

        if colour_to_cure is None:
            return False

        # Filters hand of unusable cards
        cards_removed = 0
        removed_cards = []
        for card in hand:
            if card.get_colour() == colour_to_cure:
                hand.remove(card)
                removed_cards.append(card)
                cards_removed += 1
            if cards_removed >= 5:
                break

        # Finding path to the nearest research station
        res_station_cities = self.game.get_research_stations()
        min_cost = 1000
        start_node = None
        for city in res_station_cities:
            node = self.game.find_path(acting_player.get_city(), city, hand)
            cost = node.get_total_cost()
            if cost < min_cost:
                min_cost = cost
                start_node = node

        if start_node is None:
            return False

        # Moving to city
        action_points = self.move_player(acting_player, start_node, 4)

        # Cure disease
        if action_points > 0:
            for card in removed_cards:
                acting_player.discard_card_by_name(card.get_name())
            self.game.cure_disease(colour_to_cure)

        return True

    def get_state_code(self):
        # Getting number of cubes on board
        cubes = 0
        for city in self.game.get_cities():
            for colour in Game.colours:
                cubes += city.get_cubes(colour)
        cube_str = str(cubes)
        if cubes < 10:
            cube_str = "0" + cube_str

        # Getting how many more cards of each colour needed to cure each disease
        cards_needed = {"blue": 5, "yellow": 5, "black": 5, "red": 5}
        for player in self.players:
            for colour in Game.colours:
                min_cards_needed = cards_needed[colour]
                player_cards_needed = 5
                hand = player.get_hand()
                for card in hand:
                    if card.get_colour() == colour:
                        player_cards_needed -= 1
                    if player_cards_needed <= 0:
                        break
                if player_cards_needed < min_cards_needed:
                    cards_needed[colour] = player_cards_needed
        cards_needed_str = ""
        for key in cards_needed:
            cards_needed_str += str(cards_needed[key])

        # Getting number of research stations on board
        research_stations = str(len(self.game.get_research_stations()))

        # Getting if disease is cured
        cured_str = ""
        for colour in Game.colours:
            cured = "0"
            if self.game.is_cured(colour):
                cured = "1"
            cured_str += cured

        return cube_str + cards_needed_str + research_stations + cured_str

    def give(self, acting_player):
        # Finding cards that are closests to players
        hand = acting_player.get_hand().copy()
        potential_players = []
        potential_cards = []
        min_cost = 1000
        for card in hand:
            for player in self.players:
                if player.has_name(acting_player.get_name()):
                    continue
                node = self.game.find_path(player.get_city(), card.get_city(), player.get_hand())
                cost = node.get_total_cost()
                if cost < min_cost:
                    min_cost = cost
                    potential_cards = [card]
                    potential_players = [player]
                elif cost == min_cost:
                    potential_players.append(player)
                    potential_cards.append(card)
        n = len(potential_players)
        if n <= 0:
            return False

        index = random.randint(0, n - 1)
        receiving_player = potential_players[index]
        card_to_give = potential_cards[index]
        target_city = card_to_give.get_city()

        # Moving to city
        hand.remove(card_to_give)
        start_node = self.game.find_path(acting_player.get_city(), target_city, hand)
        action_points = self.move_player(acting_player, start_node, 4)

        # Giving card, if can
        if action_points > 0 and acting_player.get_city().equals(target_city) and receiving_player.get_city().equals(
                target_city):
            acting_player.discard_card_by_name(card_to_give.get_name())
            receiving_player.add_to_hand(card_to_give)

        return True

    def initialise_q_values(self):
        data = {}

        for i in range(4*24 + 1):
            # Number of cubes on the board
            num_cubes = str(i)
            num_cubes = elongate_str(num_cubes, "0", 2)

            # Number of cards needed to cure each disease
            for j in range(6*6*6*6):
                num_cards = decimal_to_new_base(j, 6)
                num_cards = elongate_str(num_cards, "0", 4)

                # Number of research stations
                for k in range(1, 7):
                    research_stations = str(k)

                    # Disease Cured
                    for l in range(2*2*2*2):
                        num_cured = decimal_to_new_base(l, 2)
                        num_cured = elongate_str(num_cured, "0", 4)

                        # Possible actions
                        state = num_cubes + num_cards + research_stations + num_cured
                        data[state] = []
                        for action in QLearningAgent2.possible_actions_str:
                            data[state].append({"action": action, "value": 0})

        with open(self.learning_file, 'w') as learning_file:
            json.dump(data, learning_file)
        return

    def is_city_in_hand(self):
        return False

    def learn(self):
        with open(self.learning_file, 'w') as learning_file:
            json.dump(self.q_values, learning_file)
        return

    def move_player(self, acting_player, current_node, action_points):
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            acting_player.move_to(current_node.get_city())
            card_used = current_node.get_used_card()
            if card_used is not None:
                acting_player.discard_card_by_name(card_used.get_name())

            action_points -= 1

        return action_points

    def observe_reward(self):
        next_state = self.get_state_code()

        cured_reward = 2
        win_reward = 10

        # Getting reward
        reward = 0
        # Has cured each disease
        for i in range(7, 11):
            if self.current_state[i] == "0" and next_state[i] == "1":
                reward += cured_reward
        # Game Won
        if self.game.all_cured():
            reward += win_reward

        # Q-learning step
        max_action_value = -1
        for action_value in self.q_values[next_state]:
            value = action_value["value"]
            if value > max_action_value:
                max_action_value = value

        for action_value in self.q_values[self.current_state]:
            if action_value["action"] == self.last_action:
                current_value = action_value["value"]
                action_value["value"] = current_value + self.alpha * (
                        reward + self.gamma * max_action_value - current_value)
                q_value = action_value["value"]
                break

        print("Q_value for " + self.current_state + ", " + self.last_action + " = " + str(q_value))
        self.current_state = next_state

        return q_value

    def q_learner_reset(self, new_game, new_window, new_start_city):
        self.reset_game(new_game, new_window, new_start_city)
        self.current_state = self.get_state_code()
        self.last_action = None
        return

    def take(self, acting_player):
        # Determines if a player is in a city that they have a card for
        potential_players = []
        for player in self.players:
            if player.has_name(acting_player.get_name()):
                continue
            if player.is_city_in_hand():
                potential_players.append(player)
        if len(potential_players) <= 0:
            return False

        # Finding closest player that matches criteria
        start_node = None
        min_cost = 1000
        hand = acting_player.get_hand()
        for player in potential_players:
            node = self.game.find_path(acting_player.get_city(), player.get_city(), hand)
            cost = node.get_total_cost()
            if cost < min_cost:
                min_cost = cost
                start_node = node
                player_to_take_from = player

        if start_node is None:
            return False

        # Moving to player
        action_points = self.move_player(acting_player, start_node, 4)

        # Taking card
        if action_points > 0:
            hand = player_to_take_from.get_hand()
            for card in hand:
                if card.get_name() == player_to_take_from.get_city().get_name():
                    card_to_take = card
                    break
            player_to_take_from.discard_card_by_name(player_to_take_from.get_city().get_name())
            acting_player.add_to_hand(card_to_take)

        return True

    def treat(self, acting_player):
        # Getting infected cites
        infected_cites = []
        cities_found = False
        for city in self.game.get_cities():
            for colour in Game.colours:
                if city.get_cubes(colour) > 0:
                    infected_cites.append(city)
                    cities_found = True
        if not cities_found:
            return False

        # Finding closest city and path to it
        chosen_city = None
        start_node = None
        min_cost = 1000
        hand = acting_player.get_hand()
        for city in infected_cites:
            node = self.game.find_path(acting_player.get_city(), city, hand)
            cost = node.get_total_cost()
            if cost < min_cost:
                min_cost = cost
                start_node = node
                chosen_city = city
        if start_node is None:
            return False

        # Moving to city
        action_points = self.move_player(acting_player, start_node, 4)

        # Treating disease
        while action_points > 0:
            cure_colour = None
            max_cubes = 0
            for colour in Game.colours:
                cubes = chosen_city.get_cubes(colour)
                if cubes > max_cubes:
                    cure_colour = colour
                    max_cubes = cubes
            if cure_colour is None:
                return True
            self.game.treat_disease(chosen_city, cure_colour)
            action_points -= 1

        return True

    def update_state(self):
        self.current_state = self.get_state_code()
        return
