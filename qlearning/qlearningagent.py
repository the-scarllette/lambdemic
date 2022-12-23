import random as rand


class QlearningAgent:

    def __init__(self, action_shape,
                 alpha=0.001, gamma=0.9, epsilon=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.action_shape = action_shape

        self.q_table = {}
        return

    def choose_action(self, state, possible_actions):
        state = state.tobytes()
        try:
            action_values = self.q_table[state]
        except KeyError:
            self.q_table[state] = [0 for _ in range(self.action_shape)]
            action_values = self.q_table[state]

        num_possible_actions = len(possible_actions)
        if num_possible_actions <= 0:
            return rand.randint(0, self.action_shape - 1)

        if rand.uniform(0, 1) <= self.epsilon:
            return rand.choice(possible_actions)

        max_value = action_values[possible_actions[0]]
        action_choices = [possible_actions[0]]
        for i in range(1, num_possible_actions):
            action = possible_actions[i]
            value = action_values[action]
            if value > max_value:
                max_value = value
                action_choices = [action]
            elif value == max_value:
                action_choices.append(action)
        return rand.choice(action_choices)

    def learn(self, state, action, reward, next_state):
        state = state.tobytes()
        next_state = next_state.tobytes()

        try:
            current_value = self.q_table[state][action]
        except KeyError:
            self.q_table[state] = [0 for _ in range(self.action_shape)]
            current_value = 0

        try:
            next_state_values = self.q_table[next_state]
        except KeyError:
            self.q_table[next_state] = [0 for _ in range(self.action_shape)]
            next_state_values = self.q_table[next_state]
        max_q_value = next_state_values[0]
        for value in next_state_values:
            if value > max_q_value:
                max_q_value = value

        self.q_table[state][action] = current_value + self.alpha * (
                reward + (self.gamma * max_q_value) - current_value)
        return
