from city import City


class Game:

    all_colours = ['blue', 'yellow', 'black', 'red']



    def __init__(self, colours=all_colours):
        self.window = None
        self.colours = colours



        return

    # Add get actions
    def get_action_space(self):
        return

    # Add get after state
    def get_after_state(self, action):
        after_state = None
        return after_state

    # Add get state space
    def get_state_space(self):
        return

    # Add step
    def step(self, action):
        next_state, reward, terminal, info = None
        return next_state, reward, terminal, info

    # Add reset
    def reset(self):
        state = None
        return state