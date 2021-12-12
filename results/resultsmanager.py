import json
import matplotlib.pyplot as plt


class ResultsManager:

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__returns_sum = 0
        self.__turn_count = 0
        return

    def add_return(self, value):
        self.__returns_sum += value
        return

    def graph_results(self):
        with open(self.__file_name) as json_file:
            graph_data = json.load(json_file)

        y = []
        for data in graph_data["run"]:
            y.append(data["return"])
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('return sum')
        plt.title('Return Sum')

        plt.show()
        return

    def write_data(self):
        with open(self.__file_name, 'r') as json_file:
            data = json.load(json_file)

        new_data = {"run": []}
        new_data["run"].append({'turn_count': self.__turn_count,
                                'return': self.__returns_sum})
        data.update(new_data)

        with open(self.__file_name, 'w') as json_file:
            json.dump(data, json_file)

        return
