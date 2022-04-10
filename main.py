from game_v2 import Game
import random as rand


def main():
    print_states = True
    print_actions = True

    num_episodes = 1000

    colours = ['blue']

    env = Game(colours)
    action_space = env.get_action_shape()

    for _ in range(num_episodes):
        done = False
        state = env.reset()
        if print_states:
            env.print_current_state()
        while not done:
            action = rand.randint(0, action_space - 1)
            next_state, reward, done, _ = env.step(action, print_actions)
            state = next_state
            if print_states:
                env.print_current_state()

    return


if __name__ == "__main__":
    main()
