from neuralnode import NeuralNode
import numpy as np


def ramp(x):
    if x <= 0:
        return 0
    return x


class NeuralNet:

    activation_functions = {'ramp': ramp}

    def __init__(self, rows, columns, weight_data='', function=ramp):
        # Declaring Variables
        self.__rows = rows
        self.__columns = columns
        self.__output_node = []
        self.__output_node = None
        self.__weights = []
        self.__activation_function = function
        self.__nodes = [[] for i in range(self.__columns)]

        # Generating weight data
        if weight_data == '':
            self.generate_weights()

        # Building network
        for i in range(self.__columns-1):
            input_node = i == 0
            last_nodes = None
            if not input_node:
                last_nodes = self.__nodes[i - 1]
            for j in range(self.__rows):
                node = NeuralNode(self.__weights[i][j], last_nodes, input_node,
                                  self.__activation_function)
                self.__nodes[i].append(node)
                if input_node:
                    self.__input_nodes.append(node)
        self.__output_node = NeuralNode(self.__weights[self.__columns-1][0], last_nodes, False,
                                        self.__activation_function)
        self.__nodes[self.__columns-1].append(self.__output_node)
        return

    def generate_weights(self):
        self.__weights = [[[] for j in range(self.__rows)] for i in range(self.__columns - 1)]
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                num_weights = self.__columns
                if i == 0:
                    num_weights = 1
                self.__weights[i][j] = np.random.uniform(0, 1, num_weights)
        self.__weights.append([np.random.uniform(0, 1, 1)])

        return

    def compute_net(self, x):
        self.__output_node.compute()
        return
