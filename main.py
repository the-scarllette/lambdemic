
from graphing import graph_local_average, graph_cured_diseases, graph_rolling_winrate
from pandemicgame import PandemicGame
from qlearning.qlearningagent import QlearningAgent

import json
import matplotlib.pyplot as plt
import random as rand


def get_run_data(filename, colours):
    env = Game(colours)
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("No Matching File Found")
        return

    return_sum_data = []
    turns_survived_data = []
    diseases_cured = []
    actions_taken = []
    num_colours = len(colours)

    for episode in data:
        total_reward = 0
        turns_survived = 0
        actions = []
        cured = []

        for trajectory in data[episode]:
            total_reward += trajectory['reward']
            turns_survived += 1
            actions.append(env.get_action_type(trajectory['action']))
        last_state = trajectory['next_state']
        index = len(last_state) - num_colours
        for i in range(num_colours):
            if last_state[index + i] == 1.0:
                cured.append(colours[i])

        return_sum_data.append(total_reward)
        turns_survived_data.append(turns_survived)
        diseases_cured.append(cured)
        actions_taken.append(actions)
    return return_sum_data, turns_survived_data, diseases_cured, actions_taken


def run_controlled_state(name, colours, epsilon, net_layers):
    print_values = True

    env = Game(colours)
    action_shape = env.get_action_shape()
    state_shape = env.get_state_shape()

    agent = TDLambdaAgent(state_shape, action_shape, epsilon=epsilon, net_layers=net_layers,
                          experience_replay=True,
                          use_target_network=False,
                          initialise=False,
                          check_point_name=name + "_data/cp.ckpt")

    state = env.reset(specify_sate=True)
    done = False
    env.print_current_state()
    while not done:
        possible_actions, possible_after_states = env.get_actions_and_after_states()
        print("Action Key:")
        for a in possible_actions:
            print(str(a) + ": " + env.get_action_string(a))
        action = agent.choose_action(possible_actions, possible_after_states, print_values=print_values)

        next_state, reward, done, info = env.step(action, True, True)
        env.print_current_state()
        state = next_state
    return


def run_dqn(random_episodes, training_episodes, colours, graph_rewards, print_states, print_actions,
            save_trajectory=True):
    env = Game(colours)
    action_shape = env.get_action_shape()
    state_shape = env.get_state_shape()

    name = 'DQN Agent'
    for colour in colours:
        name += " " + colour

    agent = DQNAgent(state_shape, action_shape)

    rewards = []
    trajectory_data = {}

    num_episodes = random_episodes + training_episodes
    for episode in range(num_episodes):
        learn = episode >= random_episodes
        done = False

        state = env.reset()
        if print_states:
            env.print_current_state()
        total_reward = 0
        turn_count = 0
        if learn:
            trajectory_data[episode - random_episodes] = []
        while not done:
            if turn_count > 10:
                print("HERE")
            action = agent.choose_action(state, random_actions=not learn)
            next_state, reward, done, info = env.step(action, print_actions)
            if print_states:
                env.print_current_state()

            agent.save_trajectory(state, action, reward, next_state, done)
            trajectory_data[episode - random_episodes].append({'state': state.tolist(),
                                                               'action': action,
                                                               'reward': reward,
                                                               'next_state': next_state.tolist(),
                                                               'terminal': done})

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
    if save_trajectory:
        with open(name + '.json', 'w') as file:
            json.dump(trajectory_data, file)
    return


def run_random(num_episodes, colours, graph_rewards, print_states, print_actions, save_trajectory):
    env = Game(colours)
    action_shape = env.get_action_shape()

    rewards = []
    cures = []
    turns_survived = []
    trajectory_data = {}

    for episode in range(num_episodes):
        done = False
        state = env.reset()
        if print_states:
            env.print_current_state()
        steps = 0
        total_reward = 0
        trajectory_data[episode] = []
        while not done:
            action = rand.randint(0, action_shape - 1)

            next_state, reward, done, info = env.step(action, print_actions)
            if print_states:
                env.print_current_state()

            trajectory_data[episode].append({'state': state.tolist(),
                                             'action': action,
                                             'reward': reward,
                                             'next_state': next_state.tolist(),
                                             'terminal': done})

            state = next_state
            total_reward += reward
            steps += 1
        rewards.append(total_reward)
        cures.append(info['cured_diseases'])
        turns_survived.append(steps)

        print("Episode finished, total reward: " + str(total_reward))
        print("Turns survived: " + str(steps))
        print("End game because " + info['terminal_reason'])

    name = 'random agent'
    if graph_rewards:
        for colour in colours:
            name += ' ' + colour
        graph_local_average(rewards, c=num_episodes / 100, name=name + " return sum")
        graph_cured_diseases(cures, colours, name=name)
        graph_local_average(turns_survived, c=num_episodes / 100, name=(name + " turns survived"))

    if save_trajectory:
        with open(name + '.json', 'w') as file:
            json.dump(trajectory_data, file)
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
    colours_to_use = ['blue']

    env = PandemicGame(colours_to_use, player_count=2, num_epidemics=4)

    agent = QlearningAgent(env.num_actions, alpha=0.9, gamma=0.9, epsilon=0.1)

    training_episodes = 10000

    returns_per_episode = []
    successes_per_episode = []

    for _ in range(training_episodes):
        total_return = 0
        done = False
        state = env.reset()
        while not done:
            possible_actions = env.get_current_possible_actions()
            action = agent.choose_action(state, possible_actions)

            next_state, reward, done, info = env.step(action)
            total_return += reward

            agent.learn(state, action, reward, next_state)
            state = next_state

        returns_per_episode.append(total_return)
        successes_per_episode.append(info['success'])

    graph_local_average(returns_per_episode, c=1, name='Returns per episode')
    graph_rolling_winrate(successes_per_episode, 10, 'Winrate')
    return


if __name__ == "__main__":
    main()
