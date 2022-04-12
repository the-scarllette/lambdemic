from game_v2 import Game
from graphing import graph_local_average, graph_cured_diseases
from dqn.dqn_agent import DQNAgent
from td_lambda.tdlambda import TDLambdaAgent


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


def run_td_lambda(random_episodes, training_episodes, colours, graph_rewards, print_states, print_actions,
                  epsilon=None, epsilon_reduction=None):
    env = Game(colours)
    action_shape = env.get_action_shape()
    state_shape = env.get_state_shape()

    using_epsilon_reduction = epsilon is not None

    agent = TDLambdaAgent(state_shape, action_shape, epsilon=epsilon,
                          experience_replay=True)
    if using_epsilon_reduction:
        agent.set_epsilon(epsilon)
        new_epsilon = epsilon

    num_episodes = random_episodes + training_episodes
    rewards = []
    cures = []

    for episode in range(num_episodes):
        learn = episode >= random_episodes
        done = False
        state = env.reset()
        agent.reset_for_next_episode()

        total_reward = 0
        if print_states:
            env.print_current_state()
        while not done:
            possible_actions, possible_after_states = env.get_actions_and_after_states()
            action = agent.choose_action(possible_actions, possible_after_states, not learn)

            next_state, reward, done, info = env.step(action, print_actions)
            if print_states:
                env.print_current_state()

            agent.save_trajectory(state, action, reward, next_state, done)

            if learn:
                agent.learn()
            state = next_state
            total_reward += reward

        if learn:
            rewards.append(total_reward)
            cures.append(info['cured_diseases'])
        print("Episode finished, total reward: " + str(total_reward))
        print("End game because " + info['terminal_reason'])

        if using_epsilon_reduction:
            new_epsilon *= epsilon_reduction
            agent.set_epsilon(new_epsilon)

    if graph_rewards:
        graph_local_average(rewards, c=training_episodes/25, name='td_lambda_agent')
        graph_cured_diseases(cures, colours)
    return


def main():
    random_episodes = 100
    training_episodes = 3000

    epsilon_start = 0.9
    epsilon_reduction = 0.999

    colours = ['blue']

    graph_rewards = True
    print_states = False
    print_actions = True

    run_td_lambda(random_episodes, training_episodes, colours,
                  graph_rewards, print_states, print_actions,
                  epsilon_start, epsilon_reduction)
    return


if __name__ == "__main__":
    main()
