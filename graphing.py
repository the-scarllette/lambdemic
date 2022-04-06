import matplotlib.pyplot as plt


def graph_local_average(data, c=10):
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
    plt.show()
    return
