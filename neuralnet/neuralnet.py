from neuralnet.neuralnode import NeuralNode
import numpy as np


class NeuralNet:

    def __init__(self, columns, rows, weight_data=''):
        # Declaring Variables
        self.__rows = rows
        self.__columns = columns
        self.__output_node = []
        self.__output_node = None
        self.__weights = []
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
                node = NeuralNode(self.__weights[i][j], last_nodes, input_node)
                self.__nodes[i].append(node)
        self.__output_node = NeuralNode(self.__weights[self.__columns-1][0], last_nodes, False)
        self.__nodes[self.__columns-1].append(self.__output_node)
        return

    def generate_weights(self):
        self.__weights = [[[] for j in range(self.__rows)] for i in range(self.__columns - 1)]
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                num_weights = self.__rows
                if i == 0:
                    num_weights = 1
                self.__weights[i][j] = np.random.uniform(0, 1, num_weights)
        self.__weights.append([np.random.uniform(0, 1, self.__rows)])

        return

    def compute_net(self, x):
        result = [self.__nodes[0][i].compute(x[i]) for i in range(self.__rows)]

        for i in range(1, self.__columns - 1):
            current_result = [self.__nodes[i][j].compute(result) for j in range(self.__rows)]
            result = current_result.copy()

        return self.__output_node.compute(result)

    def print_weights(self):
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                print("Node " + str(i) + ", " + str(j) + " weights: " + str(self.__weights[i][j]))
        print("Node " + str(self.__columns - 1) + ", " + str(0) + " weights: " + str(self.__weights[i][0]))
        return

    def set_node_weights(self, i, j, new_weights):
        self.__nodes[i][j].set_weights(new_weights)
        return
