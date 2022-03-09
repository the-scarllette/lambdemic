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
        num_cites = len(self.game.get_cities())
        return
