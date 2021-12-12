from learningagent import LearningAgent
from game import Game
from generalfunctions import decimal_to_binary
import random
import json

'''Data stored on environment:
        How many cities infected
        Do we have enough cards to cure
        Cured diseases
    
    States encoded as:
        {NUMCITES}{0/1CureBlue}{0/1CureYellow}{0/1CureBlack}{01/CureRed
        {0/1CuredBlue}{{0/1CuredYellow}{0/1CuredBlack}{01/CuredRed}} 
    
    Possible Actions:
        treat
            Moves to closest city with disease cubes
            Removes as many cubes as possible
        build
            Moves to closest card location
            Builds research station there if there isn't already one
        give
            If other player is in city of matching card
            moves to closest player that matches criteia
            gives card
        take
            If player has card of the city they are in
            Moves to the closest player that matches this cretieria
            Takes card
        cure
            If have enough cards to cure an uncured disease
            moves to research station and cures
    
    State-action space size:
        states: 48x16x16 = 12,288
        actions: 5
        state action space : 61,440
'''

class QLearningAgent(LearningAgent):
    results_file = 'results/qlearning_results.json'
    learning_file = 'qlearning/learning_data.json'

    possible_actions_str = ["treat", "build", "give", "take", "cure"]

    # Learning Rate
    alpha = 0.9

    # Epsilon in epsilon-greedy function
    epsilon = 0.2

    # Discounting Factor
    gamma = 0.5

    def __init__(self, game, player_count, window, start_city):
        super(QLearningAgent, self).__init__(game, QLearningAgent.learning_file, QLearningAgent.results_file,
                                             player_count, window, start_city)

        with open(self.learning_file) as json_file:
            self.q_values = json.load(json_file)

        self.current_state = self.get_state_code()
        self.possible_actions = {"treat": self.treat,
                                 "build": self.build,
                                 "give": self.give,
                                 "take": self.take,
                                 "cure": self.cure}
        return

    def act(self):
        action_taken = False
        unavailable_actions = []

        while not action_taken:
            # Using epsilon-greedy to determine if to take a random action
            x = random.randint(1, 100)
            if x <= self.epsilon*100:  # Take a random action
                action = random.choice(self.possible_actions_str)
            else:  # Take action that maximises reward
                action = self.choose_optimal_action(self.current_state)

            unavailable_actions.append(action)

            # Takes action
            action_taken = self.possible_actions[action](self.players[self.current_turn])

        self.current_turn = (self.current_turn + 1) % self.player_count
        return

    def build(self, acting_player):
        # Finds closest city based on cards in hand
        hand = acting_player.get_hand()
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

    def choose_optimal_action(self, current_state):
        best_action = self.possible_actions[0]
        best_q_value = -1

        for action_value in self.q_values[current_state]:
            if action_value["value"] > best_q_value:
                best_action = action_value["action"]
                best_q_value = action_value["value"]

        return best_action

    def cure(self):
        return

    def discard_card_by_name(self, card_name):
        return False

    def get_state_code(self):
        # Getting number of infected cities
        infected_cites = 0;
        for city in self.game.get_cities:
            for colour in Game.colours:
                if city.get_cubes(colour) > 0:
                    infected_cites += 1
                    break
        infected_cites = str(infected_cites)
        if len(infected_cites) < 2:
            infected_cites = "0" + infected_cites

        # Getting If we can cure each disease
        can_cure = {"blue": 0, "yellow": 0, "black": 0, "red": 0}
        for player in self.players:
            hand = player.get_hand()
            for colour in Game.colours:
                count = 0
                for card in hand:
                    if card.get_colour().equals(colour):
                        count += 1
                if count >= 5:
                    can_cure[colour] = 1
        can_cure_str = ""
        for key in can_cure:
            can_cure_str += str(can_cure[key])

        # Getting if disease is cured
        cured_str = ""
        for colour in Game.colours:
            cured = "0"
            if self.game.is_cured(colour):
                cured = "1"
            cured_str += cured

        return infected_cites + can_cure_str + cured_str

    def give(self):
        return

    def initialise_q_values(self):
        data = {}
        for i in range(len(self.game.get_cities())):
            # Number of infected cities
            num_cities = str(i)
            if len(num_cities) <= 1:
                num_cities = "0" + num_cities

            # Can cure a disease and disease cured
            for j in range(2556):
                cured_num = decimal_to_binary(j)
                while len(cured_num) < 8:
                    cured_num = "0" + cured_num

                # Possible Actions
                # Add possible actions
                state = num_cities + cured_num
                data[state] = []
                for action in QLearningAgent.possible_actions_str:
                    data[state].append({"action" : action, "value": 0})

        with open(self.learning_file, 'w') as learning_file:
            json.dump(data, learning_file)
        return

    def is_city_in_hand(self):
        return False

    def move_player(self, acting_player, current_node, action_points):
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            acting_player.move_to(current_node.get_city())
            card_used = current_node.get_used_card()
            if card_used is not None:
                acting_player.discard_card_by_name(card_used.get_name())

            action_points -= 1

        return action_points

    def take(self):
        return

    def treat(self):
        return
