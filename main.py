from game_v2 import Game
from graphing import graph_local_average, graph_cured_diseases
from dqn.dqn_agent import DQNAgent
from td_lambda.tdlambda import TDLambdaAgent
from qlearning.qlearningagent import QlearningAgent
import random as rand
import json


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
        graph_local_average(rewards, c=training_episodes / 25)
    return


def run_q_learning(num_episodes, colours,
                   graph_rewards, print_states, print_actions, save_trajectory):
    env = Game(colours)
    action_shape = env.get_action_shape()

    rewards = []
    cures = []
    turns_survived = []
    trajectory_data = {}

    agent = QlearningAgent(action_shape)
    name = 'q_learning_agent ' + str(num_episodes)
    for colour in colours:
        name += ' ' + colour
    for episode in range(num_episodes):
        done = False
        state = env.reset()
        if print_states:
            env.print_current_state()
        steps = 0
        total_reward = 0
        trajectory_data[episode] = []
        while not done:
            possible_actions, _ = env.get_actions_and_after_states()
            action = agent.choose_action(state, possible_actions)

            next_state, reward, done, info = env.step(action, print_actions)
            trajectory_data[episode].append({'state': state.tolist(),
                                             'action': action,
                                             'reward': reward,
                                             'next_state': next_state.tolist(),
                                             'terminal': done})
            if print_states:
                env.print_current_state()

            agent.learn(state, action, reward, next_state)
            state = next_state
            total_reward += reward
            steps += 1

        rewards.append(total_reward)
        cures.append(info['cured_diseases'])
        turns_survived.append(steps)
        print("Episode finished, total reward: " + str(total_reward))
        print("Turns survived: " + str(steps))
        print("End game because " + info['terminal_reason'])

    if graph_rewards:
        graph_local_average(rewards, c=10, name=name + " return sum")
        graph_cured_diseases(cures, colours, name=name)
        graph_local_average(turns_survived, c=10, name=(name + " turns survived"))

    if save_trajectory:
        with open(name + '.json', 'w') as file:
            json.dump(trajectory_data, file)
    return


def run_random(num_episodes, colours, graph_rewards, print_states, print_actions):
    env = Game(colours)
    action_shape = env.get_action_shape()

    rewards = []
    cures = []
    turns_survived = []

    for _ in range(num_episodes):
        done = False
        state = env.reset()
        if print_states:
            env.print_current_state()
        steps = 0
        total_reward = 0
        while not done:
            action = rand.randint(0, action_shape - 1)

            next_state, reward, done, info = env.step(action, print_actions)
            if print_states:
                env.print_current_state()

            state = next_state
            total_reward += reward
            steps += 1
        rewards.append(total_reward)
        cures.append(info['cured_diseases'])
        turns_survived.append(steps)

        print("Episode finished, total reward: " + str(total_reward))
        print("Turns survived: " + str(steps))
        print("End game because " + info['terminal_reason'])

    if graph_rewards:
        name = 'random agent'
        for colour in colours:
            name += ' ' + colour
        graph_local_average(rewards, c=num_episodes / 100, name=name + " return sum")
        graph_cured_diseases(cures, colours, name=name)
        graph_local_average(turns_survived, c=num_episodes / 100, name=(name + " turns survived"))
    return


def run_td_lambda(random_episodes, training_episodes, colours, graph_rewards, print_states, print_actions,
                  net_layer, epsilon=None, epsilon_reduction=None,
                  use_target_network=False,
                  name_prefix='',
                  save_trajectory=False):
    env = Game(colours)
    action_shape = env.get_action_shape()
    state_shape = env.get_state_shape()

    using_epsilon_reduction = epsilon_reduction is not None

    name = name_prefix + 'td_lambda_agent ' + str(training_episodes)
    for colour in colours:
        name += ' ' + colour
    if using_epsilon_reduction:
        name += ' with epsilon reduction'
    if use_target_network:
        name += ' with target network'

    agent = TDLambdaAgent(state_shape, action_shape, epsilon=epsilon, net_layers=net_layer,
                          experience_replay=random_episodes > 0,
                          use_target_network=use_target_network,
                          check_point_name=name + "_data/cp.ckpt", checkpoint_step=500)
    if using_epsilon_reduction:
        agent.set_epsilon(epsilon)
        new_epsilon = epsilon

    num_episodes = random_episodes + training_episodes
    rewards = []
    cures = []
    turns_survived = []
    trajectory_data = {}

    for episode in range(num_episodes):
        learn = episode >= random_episodes
        done = False
        state = env.reset()
        agent.reset_for_next_episode()

        total_reward = 0
        if print_states:
            env.print_current_state()
        steps = 0
        if learn:
            trajectory_data[episode - random_episodes] = []
        while not done:
            possible_actions, possible_after_states = env.get_actions_and_after_states()
            action = agent.choose_action(possible_actions, possible_after_states, not learn)

            next_state, reward, done, info = env.step(action, print_actions)
            if learn:
                trajectory_data[episode - random_episodes].append({'state': state.tolist(),
                                                                   'action': action,
                                                                   'reward': reward,
                                                                   'next_state': next_state.tolist(),
                                                                   'terminal': done})

            if print_states:
                env.print_current_state()

            agent.save_trajectory(state, action, reward, next_state, done)

            if learn:
                agent.learn()
            state = next_state
            total_reward += reward
            steps += 1

        if learn:
            rewards.append(total_reward)
            cures.append(info['cured_diseases'])
            turns_survived.append(steps)
        print("Episode finished, total reward: " + str(total_reward))
        print("Turns survived: " + str(steps))
        print("End game because " + info['terminal_reason'])

        if using_epsilon_reduction:
            new_epsilon *= epsilon_reduction
            agent.set_epsilon(new_epsilon)

    if graph_rewards:
        graph_local_average(rewards, c=training_episodes / 50, name=name + " return sum")
        graph_cured_diseases(cures, colours, name=name)
        graph_local_average(turns_survived, c=training_episodes / 50, name=(name + " turns survived"))

    if save_trajectory:
        with open(name + '.json', 'w') as file:
            json.dump(trajectory_data, file)
    return


def main():
    random_episodes = 10000
    training_episodes = 6000
    possible_colours = [['blue', 'yellow']]

    net_layer = [64, 32, 16]
    use_target_network = False

    graph_rewards = True
    print_states = False
    print_actions = False

    for colours in possible_colours:
        run_td_lambda(random_episodes, training_episodes, colours,
                      graph_rewards, print_states, print_actions,
                      net_layer=net_layer, epsilon=0.1, epsilon_reduction=None,
                      use_target_network=use_target_network,
                      name_prefix=str(net_layer),
                      save_trajectory=True)

    return


if __name__ == "__main__":
    main()
