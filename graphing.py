import matplotlib.pyplot as plt


def graph_cured_diseases(data, all_colours):
    labels = ['None'] + all_colours
    sizes_dict = {label: 0 for label in labels}

    for elm in data:
        if len(elm) <= 0:
            sizes_dict['None'] += 1
            continue
        for colour in elm:
            sizes_dict[colour] += 1

    sizes = [sizes_dict[label] for label in labels]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('TD(Lambda) total runs ' + str(len(data)))
    plt.show()
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

    plt.plot(x, y)
    plt.ylabel('Total Episode Reward')
    plt.xlabel('Run Number')
    if name is not None:
        plt.title(name)
    plt.show()
    return
