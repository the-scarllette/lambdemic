import json
import matplotlib.pyplot as plt


def pie_chart_cures(data):
    labels = ['0', '1', '2', '3', '4']
    sizes = [0 for i in range(5)]

    for run in data["run"]:
        sizes[run["cured_diseases"]] += 1

    # Removing 0 sizes
    i = 4
    while i >= 0:
        if sizes[i] <= 0:
            del(sizes[i])
            del(labels[i])
        i -= 1

    plot_pie_chart(labels, sizes)
    return


def plot_pie_chart(labels, sizes):
    total = sum(sizes)

    print("Cure data results")
    print("Total results " + str(total))
    for i in range(len(sizes)):
        print(labels[i] + " - " + str(sizes[i]))

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct=lambda p: '{:.0f}'.format(p * total / 100),
            shadow=True, startangle=90)
    ax1.axis('equal')

    plt.show()
    return


class ResultsManager:

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__returns_sum = 0
        self.__turn_count = 0
        return

    def add_return(self, value):
        self.__returns_sum += value
        return

    def get_cured_data(self):
        with open(self.__file_name) as json_file:
            graph_data = json.load(json_file)

        cured_array = [0, 0, 0, 0, 0]
        total_runs = 0

        for data in graph_data["run"]:
            cured_array[data["cured_diseases"]] += 1
            total_runs += 1

        print("total runs: " + str(total_runs))
        print(cured_array)
        return

    def graph_and_save(self, filename):
        with open(self.__file_name) as json_file:
            graph_data = json.load(json_file)

        # Graphing Sum Return
        y = []
        for data in graph_data["run"]:
            y.append(data["return"])
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('return sum')
        plt.title('Return Sum')
        # Saving Return Sum Graph
        plt.savefig(filename)

        # Graphing cures as pie chart
        pie_chart_cures(graph_data)
        return

    def graph_results(self):
        with open(self.__file_name) as json_file:
            graph_data = json.load(json_file)

        # Printing number of runs
        print("Number of runs: " + str(len(graph_data["run"])))

        # Graphing Infected Cities
        y = []
        for data in graph_data["run"]:
            y.append(data["infected_cities"])
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('infected cities at run end')
        plt.title('Infected Cities at run end')

        plt.show()

        self.graph_and_save('return_sum.pdf')

        # Graphing turns survived
        y = []
        for data in graph_data["run"]:
            y.append(data["turn_count"])
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('Turns Survived')
        plt.title('Turns survived')

        plt.show()
        return

    def increment_turn_count(self):
        self.__turn_count += 1
        return

    def split_graph(self):
        index = 100285 - 40000

        with open(self.__file_name) as json_file:
            graph_data = json.load(json_file)

        # Graphing Sum Return
        y = []
        i = 0
        for data in graph_data["run"]:
            if i >= index:
                y.append(data["return"])
            i += 1
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('return sum')
        plt.title('Return Sum')
        plt.savefig('return_sum_02.pdf')

        # Graphing Cures
        labels_1 = ['0', '1', '2', '3', '4']
        sizes_1 = [0 for i in range(5)]

        i = 0
        for run in graph_data["run"]:
            if i >= index:
                sizes_1[run["cured_diseases"]] += 1
            i += 1

        # Removing 0 sizes
        i = 4
        while i >= 0:
            if sizes_1[i] <= 0:
                del (sizes_1[i])
                del (labels_1[i])
            i -= 1

        plot_pie_chart(labels_1, sizes_1)
        return

    def write_data(self, infected_cities=0, cured_diseases=0):
        with open(self.__file_name, 'r') as json_file:
            data = json.load(json_file)

        data["run"].append({'turn_count': self.__turn_count,
                            'infected_cities': infected_cities,
                            'cured_diseases': cured_diseases,
                            'return': self.__returns_sum})

        with open(self.__file_name, 'w') as json_file:
            json.dump(data, json_file)

        return
