import matplotlib.pyplot as plt
from itertools import chain, combinations
import numpy as np

colordict = {'None': '#939191',
             'blue': 'blue',
             'yellow': '#E1DA08',
             'black': 'black',
             'red': 'red',
             'blueyellow': '#08E14C',
             'blueblack': '#B206C0',
             'bluered': '#EF32C2',
             'yellowblack': '#F2A630',
             'yellowred': '#F27230',
             'blackred': '#A03701',
             'blueyellowblack': '#15D0E6',
             'blueyellowred': '#04c477',
             'blueblackred': '#15E68C',
             'yellowblackred': '#60E615',
             'blueyellowblackred': '#F5D2F5'
             }

colours_combo = [key for key in colordict]

action_colours = {'cure': 'blue',
                  'give': 'red',
                  'take': 'green',
                  'treat': 'magenta'}


def powerset(iterable):
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


def graph_actions_taken(data, name, last_n=None):
    if last_n is not None:
        n = len(data) - last_n
        new_data = [data[n + i] for i in range(last_n)]
        data = new_data

    num_episodes = len(data)

    labels = [label for label in action_colours]
    sizes_dict = {label: 0 for label in labels}

    for episode in data:
        for elm in episode:
            sizes_dict[elm] += 1

    sizes = [sizes_dict[key] for key in sizes_dict]

    fig1, ax1 = plt.subplots()
    pie_wedge_collection = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title(name)
    plt.savefig(name + ".png")
    return


def graph_cures_barchart(data, all_colours, name, last_n=None):
    if last_n is not None:
        n = len(data) - last_n
        new_data = [data[n + i] for i in range(last_n)]
        data = new_data

    to_graph = {colour: [int(colour in elm) for elm in data] for colour in all_colours}
    x = [i for i in range(len(data))]

    fig, ax = plt.subplots()
    num_colours = len(all_colours)
    colour = all_colours[0]
    ax.bar(x, to_graph[colour], width=2.0)
    bottom_bar = [0 for _ in range(len(data))]
    for i in range(1, num_colours):
        colour = all_colours[i]
        bottom_bar = np.add(bottom_bar, to_graph[all_colours[i - 1]]).tolist()
        ax.bar(x, to_graph[colour], width=2.0, bottom=bottom_bar, color=colour)
    ax.set_ylabel('Cures')
    ax.set_xlabel('Episode')
    ax.set_title(name)
    ax.autoscale(tight=True)

    plt.savefig(name + '.png')
    return


def graph_cured_diseases(data, all_colours, name, last_n=None):
    s = powerset(all_colours)
    labels = [[sub_elm for sub_elm in elm] for elm in s]
    labels[0] = ['None']

    sizes = [0 for _ in labels]

    if last_n is not None:
        n = len(data)
        new_data = [data[i] for i in range(last_n, n)]
        data = new_data

    for elm in data:
        if len(elm) <= 0:
            sizes[0] += 1
            continue
        for i in range(1, len(labels)):
            if elm == labels[i]:
                sizes[i] += 1
                break

    labels_str = []
    for elm in labels:
        label_str = ""
        for x in elm:
            label_str += (x + " ")
        labels_str.append(label_str)

    y = np.array(sizes)
    fig1, ax1 = plt.subplots()
    patches, texts, pcts = ax1.pie(y, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    for i in range(len(patches)):
        pie_wedge = patches[i]
        pie_wedge.set_facecolor(colordict[colours_combo[i]])
        if colours_combo[i] == 'black':
            pcts[i].set_color('white')

    porcent = 100. * y / y.sum()
    labels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(labels_str, porcent)]

    patches, labels, dummy = zip(*sorted(zip(patches, labels, y),
                                         key=lambda x: x[2],
                                         reverse=True))

    plt.legend(patches, labels, loc='lower left',
               fontsize=8)

    plt.title(name)
    plt.savefig(name + ".png")
    return


def graph_local_average(data_array=[], array_data=False, c=10, name=None):
    if not array_data:
        data_array = [data_array]

    plt.clf()
    for data in data_array:
        x = []
        y = []
        current_total = 0
        for i in range(len(data)):
            current_total += data[i]
            if i % c == 0 and i > 0:
                y.append(current_total / c)
                current_total = 0
                x.append(i)

        if i % c != 0:
            y.append(current_total / c)
            x.append(i)

        plt.plot(x, y)

    plt.xlabel('Episode Number')
    if name is not None:
        plt.title(name)
    plt.savefig(name + ".png")
    return
