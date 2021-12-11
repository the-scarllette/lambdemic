from learningagent import LearningAgent

'''Data stored on environment:
        How many cities infected
        Do we have enough cards to cure
        Cured diseases
    
    States encoded as:
        {NUMCITES}{0/1CureBlue}{0/1CureYellow}{0/1CureBlack}{01/CureRed
        {0/1CuredBlue}{{0/1CuredYellow}{0/1CuredBlack}{01/CuredRed}} 
'''

class QLearningAgent(LearningAgent):

    results_file = 'qlearning_results.json'
    learning_file = 'learning_data.json'

    def __init__(self, player_count, window, start_city):
        super().__init__(QLearningAgent.learning_file, QLearningAgent.results_file,
                         player_count, window, start_city)
        return

    def act(self):
        return 0

    def discard_card_by_name(self, card_name):
        return False

    def is_city_in_hand(self):
        return False