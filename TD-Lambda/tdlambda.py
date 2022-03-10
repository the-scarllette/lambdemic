from neuralnet.neuralnet import NeuralNet
from learningagent import LearningAgent

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

19 total inputs
'''


class TDLambda(LearningAgent):
    learning_file = 'tdlambda_learning_data.json'
    results_file = 'tdlambda_results.json'
    
    num_net_inputs = 19
    
    def __init__(self, game, alpha, lamb, net_layers, player_count, window, start_city, initialise):
        super(self).__init__(game, TDLambda.learning_file, TDLambda.results_file,
                             player_count, window, start_city)
        self.alpha = alpha
        self.lamb = lamb
        self.net_layers = net_layers
        self.net = None
        if initialise:
            self.build_neural_net()
        else:
            self.load_neural_net()
        
        self.current_state = {}
        self.cities = self.game.get_cities()
        return
    
    def act(self):
        return
    
    def build_neural_net(self):
        self.net = NeuralNet(self.net_layers, TDLambda.num_net_inputs)
        self.net.save_net(TDLambda.learning_file)
        return
    
    def choose_action(self, state):
        return
    
    def load_neural_net(self):
        self.net = NeuralNet(net_filename=TDLambda.learning_file)
        return
    
    def update_neural_net(self):
        # Terminal states are always 0 so just compares rewards
        return
    
    def update_state(self):
        colours = self.game.Colours
        
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
            for i in range(self.num_players):
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
