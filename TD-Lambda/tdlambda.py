from neuralnet.neuralnet import NeuralNet
from learningagent import LearningAgent
from numpy import random
from pathnode import PathNode
from game import Game
from generalfunctions import binary_to_decimal, new_base_to_decimal

''' State details:
blue infected cities: 2^48 x3 for 1, 2, 3 cubes
Yellow infected cities: 2^48 x3 for 1, 2, 3 cubes
Black infected cities: 2^48 x3 for 1, 2, 3 cubes
Red infected cities: 2^48 x3 for 1, 2, 3 cubes

num outbreaks: 8

research station locations: 2^48

player locations: 48^2 where player 1 is where player 2 is

player card locations: 4^48 in deck, in player1 hand, in player 2 hand, discarded

infection card locations: 2^48 in deck or discarded

epidemics in deck: 4

cured diseases: 2^4

18 + num_players total inputs

### Actions after_state

Treat(city, colour) : if city has colour disease cubes, move to it and remove as many cubes as possible
Discover_Cure(city, colour) : if city has research station and player can cure colour, move to city and cure disease
Build(city) : if player has city card, move to that city and build research station
Give(city) : if a player has that city card, go to that city and if another player is there give the card
Take(city) : if another player has a city card and is in that city, go to that city and take the card
'''


class TDLambda(LearningAgent):
    learning_file = 'tdlambda_learning_data.json'
    results_file = 'tdlambda_results.json'
    
    num_net_inputs = 18

    actions = {build: 'build', cure: 'cure', give: 'give', take: 'take', treat: 'treat'}
    
    def __init__(self, game, alpha, lamb, net_layers, player_count, window, start_city, initialise, epsilon=0.0):
        super(self).__init__(game, TDLambda.learning_file, TDLambda.results_file,
                             player_count, window, start_city)
        self.alpha = alpha
        self.lamb = lamb
        self.epsilon = epsilon
        self.net_layers = net_layers
        self.net = None
        if initialise:
            self.build_neural_net()
        else:
            self.load_neural_net()
        
        self.current_state = {}
        self.cities = self.game.get_cities()
        self.num_net_inputs = TDLambda.num_net_inputs + self.player_count
        return
    
    def act(self):
        # Chooses action
        action, after_state, params = self.choose_action()

        # Takes action

        return

    def build(self, acting_player, city):
        # Checks if player can build in city and if there is a research station already there
        if (not acting_player.is_city_in_hand(city)) or city.has_research_station():
            return None

        # Finding the shortest path to city
        hand = acting_player.get_hand().copy()
        for card in hand:
            if card.has_city(city):
                used_card = card
                hand.remove(used_card)
                break
        start_node = self.game.find_path(acting_player.get_city(), city, hand)
        
        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0:
            return after_state
        after_state['research_stations'].append(city)
        after_state['city_cards']['player_hands'][self.current_turn].remove(used_card)
        after_state['city_cards']['discarded'][acting_player_index].append(used_card)
        return after_state
    
    def build_neural_net(self):
        self.net = NeuralNet(self.net_layers, self.num_net_inputs)
        self.net.save_net(TDLambda.learning_file)
        return
    
    def choose_action(self):
        possible_actions = []
        acting_player = self.players[self.current_turn]

        # Getting all possible actions and their after_states
        for action in TDLambda.actions:
            for city in self.cities:
                takes_colour_input = True
                for colour in Game.colours:
                    if TDLambda.actions[action] == 'cure' and not acting_player.can_cure(colour):
                        continue
                    if not takes_colour_input:
                        break
                    try:
                        after_state = action(self, acting_player, city, colour)
                        params = city.get_name() + " " + colour
                    except TypeError:
                        after_state = action(self, acting_player, city)
                        params = city.get_name()
                        takes_colour_input = False
                    finally:
                        if after_state is not None:
                            possible_actions.append({'action': action, 'after_state': after_state, 'params': params})

        # Choosing which action to take
        if random.uniform([0, 1]) <= self.epsilon:  # Takes random action
            choice = random.choice(possible_actions)
            return choice['action'], choice['after_state'], choice['params']
        # Find best action and takes it
        max_value = self.compute_state_value(possible_actions[0]['after_state'])
        best_action_indexes = [0]
        for i in range(1, len(possible_actions)):
            possible_action = possible_actions[i]
            value = self.compute_state_value(possible_action['after_state'])
            if value > max_value:
                max_value = value
                best_action_indexes = [i]
            elif value == max_value:
                best_action_indexes.append(i)
        choice = possible_actions[random.choice(best_action_indexes)]
        return choice['action'], choice['after_state'], choice['params']

    def compute_state_value(self, state):
        # Converts state into inputs
        net_input = [0 for i in range(self.num_net_inputs)]

        # Infected cities
        num_colours = len(Game.colours)
        for i in range(num_colours):
            colour = Game.colours[i]
            for num_cubes in range(1, 4):
                binary_num = int(''.join([str(int(city in state['infected_cities'][colour][num_cubes]))
                                          for city in self.cities]))
                net_input[i*3 + (num_cubes - 1)] = binary_to_decimal(binary_num)

        # Number of Outbreaks
        index = num_colours*4
        net_input[index] = state['outbreaks']

        # Research Stations
        index += 1
        binary_num = int(''.join([str(int(city in state['research_stations']))
                                  for city in self.cities]))
        net_input[index] = binary_to_decimal(binary_num)

        # Player Locations
        for i in range(self.player_count):
            index += 1
            net_input[index] = self.cities.index(state['player_locations'][i])

        # Player card locations
        index += 1
        num = ['0' for city in self.cities]
        for i in range(self.player_count):
            for card in state['city_cards']['player_hands'][i]:
                num[self.cities.index(card.get_city)] = str(i + 1)
        for card in state['city_cards']['discarded']:
            num[self.cities.index(card.get_city)] = str(self.player_count)
        net_input[index] = new_base_to_decimal(''.join(num), self.player_count + 1)

        # Infection card locations
        index += 1
        num = ['0' for city in self.cities]
        for card in state['infection_cards']:
            num[self.cities.index[card.get_city()]] = '1'
        net_input[index] = binary_to_decimal(''.join(num))

        # Epidemics drawn
        index += 1
        net_input[index] = state['epidemics']

        # Cured diseases
        index += 1
        num = [str(int(colour in state['cured_diseases'])) for colour in Game.colours]
        net_input[index] = binary_to_decimal(num)

        # Runs state through neural net
        result = self.net.compute_net(net_input)
        return result

    def cure(self, acting_player, city, colour):
        # Checks if city has research station and if colour cured
        if not city.has_research_station() or colour in self.current_state['cured_diseases']:
            return None

        # Finds path to city
        hand = acting_player.get_hand().copy()
        to_remove = []
        for card in hand:
            if card.has_colour(colour):
                to_remove.append(card)
        for card in to_remove:
            hand.remove(card)
        start_node = self.game.find_path(acting_player.get_city(), city, hand)

        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0:
            return after_state
        after_state['cured_disease'].append(colour)
        cards_to_cure = 5
        while cards_to_cure > 0:
            card_to_remove = to_remove.pop()
            after_state['city_cards']['player_hands'][self.current_turn].remove(card_to_remove)
            after_state['city_cards']['discarded'].append(card_to_remove)
            cards_to_cure -= 1
        return after_state

    def find_move_after_state(self, current_node, action_points):
        after_state = self.current_state.copy()
        while action_points > 0 and current_node.get_next_node() is not None:
            current_node = current_node.get_next_node()
            card_used = current_node.get_used_card()
            if card_used is not None:
                after_state['city_cards']['player_hands'][self.current_turn].remove(card_used)
                after_state['city_cards']['discarded'].append(card_used)
            action_points -= 1
        after_state['player_locations'][self.current_state] = current_node.get_city()
        return after_state, action_points

    def give(self, acting_player, city):
        # Checks if player has the city in their hand
        if not acting_player.is_city_in_hand(city):
            return None
        
        # Finding path to city
        hand = acting_player.get_hand().copy()
        for card in hand:
            if card.has_city(city):
                giving_card = card
                hand.remove(giving_card)
                break
        start_node = self.game.find_path(acting_player.get_city(), city, hand)

        # Works out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0:
            return after_state
        player_index = -1
        for i in range(self.num_net_):
            receiving_player = self.players[i]
            if (not receiving_player.equals(acting_player)) and (receiving_player.in_city(city)):
                player_index = i
                break
        if player_index == -1:
            return after_state
        after_state['city_cards']['player_hands'][self.current_turn].remove(giving_card)
        after_state['city_cards']['player_hands'][player_index].append(giving_card)
        return after_state
    
    def load_neural_net(self):
        self.net = NeuralNet(net_filename=TDLambda.learning_file)
        return

    def take(self, acting_player, city):
        # Checks if there is a player in that city and if they have the corresponding city card in hand
        giving_player_index = None
        for i in range(self.num_net_):
            player = self.players[i]
            if (not player.equals(acting_player)) and player.has_city_in_hand() and player.in_city(city):
                giving_player_index = i
                giving_player = player
                break
        if giving_player_index is None:
            return None

        # Finding path to city
        start_node = self.game.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Working out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0:
            return after_state
        for card in giving_player.get_hand():
            if card.has_city(city):
                taking_card = card
                break
        after_state['city_cards']['player_hands'][giving_player_index].remove(taking_card)
        after_state['city_cards']['player_hands'][self.current_turn].append(taking_card)
        return after_state

    def treat(self, acting_player, city, colour):
        # Checks if city has disease cubes of given colour
        num_cubes = city.get_cubes(colour)
        if num_cubes <= 0:
            return None

        # Finding path to city
        start_node = self.game.find_path(acting_player.get_city(), city, acting_player.get_hand())

        # Working out after state
        action_points = 4
        after_state, action_points = self.find_move_after_state(start_node, action_points)
        if action_points <= 0:
            return after_state
        if self.game.is_cured(colour):
            after_state['infected_cities'][colour][num_cubes].remove(city)
            return after_state
        new_num_cubes = num_cubes - action_points
        after_state['infected_cities'][colour][num_cubes].remove(city)
        if new_num_cubes > 0:
            after_state['infected_cites'][colour][new_num_cubes].append(city)
        return after_state
    
    def update_neural_net(self):
        # Terminal states are always 0 so just compares rewards
        return
    
    def update_state(self):
        colours = Game.colours
        
        # Infected Cities
        self.current_state['infected_cities'] = {colour: {i: [city for city in self.cities if city.get_cubes(colour)]
                                                          for i in range(1, 4)} for colour in colours}
        
        # Number of outbreaks
        self.current_state['outbreaks'] = self.game.get_outbreaks()
        
        # Research stations
        self.current_state['research_stations'] = self.game.get_research_stations()
        
        # Player locations
        self.current_state['player_locations'] = [player.get_city() for player in self.players]
        
        # City card locations
        self.current_state['city_cards'] = {'player_hands': [[] for player in self.players], 'discarded': []}
        for card  in self.game.get_discarded_city_cards():
            card_added = False
            for i in range(self.player_count):
                if self.players[i].has_card(card):
                    self.current_state['city_cards']['player_hands'][i].append(card)
                    card_added = True
                    break
            if not card_added:
                self.current_state['city_cards']['discarded'].append(card)
        
        # Infection Cards in discard pile
        self.current_state['infection_cards'] = self.game.get_infection_discard_pile()
        
        # Number of epidemics drawn
        self.current_state['epidemics'] = self.game.get_epidemics()

        # Cured diseases
        self.current_state['cured_diseases'] = [colour for colour in colours if self.game.is_cured(colour)]
        return
