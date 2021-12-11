import json


class ResultsManager:

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__returns_sum = 0
        self.__turn_count = 0
        return

    def add_return(self, value):
        self.__returns_sum += value
        return

    def write_data(self):
        with open(self.__file_name, 'r') as json_file:
            data = json.load(json_file)

        new_data = {};
        new_data["run"].append({'return': self.__returns_sum,
                                'turn_count': self.__turn_count})
        data.update(new_data)

        with open(self.__file_name, 'w') as json_file:
            json.dump(data, json_file)

        return
