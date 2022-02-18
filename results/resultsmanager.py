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

    def graph_results(self):
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

        plt.show()

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

        # Graphing Cured Diseases
        y = []
        for data in graph_data["run"]:
            y.append(data["cured_diseases"])
        x = [i for i in range(len(y))]

        plt.plot(x, y)
        plt.xlabel('run number')
        plt.ylabel('cured diseases at run end')
        plt.title('Cured Diseases at run end')

        plt.show()

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

    def write_data(self, infected_cities, cured_diseases):
        with open(self.__file_name, 'r') as json_file:
            data = json.load(json_file)

        data["run"].append({'turn_count': self.__turn_count,
                            'infected_cities': infected_cities,
                            'cured_diseases': cured_diseases,
                            'return': self.__returns_sum})

        with open(self.__file_name, 'w') as json_file:
            json.dump(data, json_file)

        return
