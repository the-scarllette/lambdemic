from game_v2 import Game
from graphing import graph_local_average
from dqn.dqn_agent import DQNAgent


def run_dqn(random_episodes, training_episodes, colours, graph_rewards, print_states, print_actions):
    env = Game(colours)
    action_shape = env.get_action_shape()
    state_shape = env.get_state_shape()

    agent = DQNAgent(state_shape, action_shape)

    rewards = []

    num_episodes = random_episodes + training_episodes
    for episode in range(num_episodes):
        learn = episode >= random_episodes
        done = False

        state = env.reset()
        if print_states:
            env.print_current_state()
        total_reward = 0
        turn_count = 0
        while not done:
            if turn_count > 10:
                print("HERE")
            action = agent.choose_action(state, random_actions=not learn)
            next_state, reward, done, info = env.step(action, print_actions)
            if print_states:
                env.print_current_state()

            agent.save_trajectory(state, action, reward, next_state, done)

            if learn:
                agent.learn()
            state = next_state
            total_reward += reward
            turn_count += 1
        if learn:
            rewards.append(total_reward)
        print("Episode finished, total reward: " + str(total_reward))
        print("End game because " + info['terminal_reason'])

    if graph_rewards:
        graph_local_average(rewards, c=training_episodes/25)
    return


def main():
    random_episodes = 30
    training_episodes = 5000

    colours = ['blue']

    graph_rewards = True
    print_states = False
    print_actions = True

    run_dqn(random_episodes, training_episodes, colours,
            graph_rewards, print_states, print_actions)
    return


if __name__ == "__main__":
    main()
