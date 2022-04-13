import matplotlib.pyplot as plt
from itertools import chain, combinations


def powerset(iterable):
    s = list(iterable)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))


def graph_cured_diseases(data, all_colours, name):
    s = powerset(all_colours)
    labels = [[sub_elm for sub_elm in elm] for elm in s]
    labels[0] = ['None']

    sizes = [0 for _ in labels]

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
            label_str += x
        labels_str.append(label_str)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels_str, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title(name + ' total runs ' + str(len(data)))
    plt.savefig(name + ".png")
    return


def graph_local_average(data, c=10, name=None):
    current_total = 0

    x = []
    y = []
    for i in range(len(data)):
        current_total += data[i]
        if i % c == 0 and i > 0:
            y.append(current_total / c)
            current_total = 0
            x.append(i)

    if i % c != 0:
        y.append(current_total / c)
        x.append(i)

    plt.clf()
    plt.plot(x, y)
    plt.xlabel('Run Number')
    if name is not None:
        plt.title(name)
    plt.savefig(name + ".png")
    return
