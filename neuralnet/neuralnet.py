from neuralnet.neuralnode import NeuralNode
import numpy as np
import json


class NeuralNet:

    def __init__(self, columns=3, rows=2, net_filename=''):
        # Loads data from file if available
        if not net_filename == '':
            try:
                with open(net_filename, "r") as net_file:
                    net_data = json.load(net_file)
                    self.__rows = net_data["rows"]
                    self.__columns = net_data["columns"]
                    self.__weights = net_data["weights"]
            except FileNotFoundError:
                raise FileNotFoundError("Net data file not found")
        else:
            self.__rows = rows
            self.__columns = columns
            self.__weights = []
            self.generate_weights()
        
        # Declaring Variables
        self.__output_node = []
        self.__output_node = None
        self.__nodes = [[] for i in range(self.__columns)]

        # Building network
        for i in range(self.__columns - 1):
            input_node = i == 0
            last_nodes = None
            if not input_node:
                last_nodes = self.__nodes[i - 1]
            for j in range(self.__rows):
                node = NeuralNode(self.__weights[i][j], i, j, last_nodes, input_node)
                self.__nodes[i].append(node)
        self.__output_node = NeuralNode(self.__weights[self.__columns - 1][0], self.__columns-1, 0,
                                        self.__nodes[self.__columns - 2], False)
        self.__nodes[self.__columns-1].append(self.__output_node)
        return

    def compute_net(self, x):
        result = [self.__nodes[0][i].compute(x[i]) for i in range(self.__rows)]

        for i in range(1, self.__columns - 1):
            current_result = [self.__nodes[i][j].compute(result) for j in range(self.__rows)]
            result = current_result.copy()

        return self.__output_node.compute(result)

    def compute_net_recursive(self, x):
        return self.__output_node.compute_recursive(x)

    def equals(self, other_net):
        other_cols, other_rows = other_net.get_size()
        if not (self.__rows == other_rows and self.__columns == other_cols):
            return False
        other_weights = other_net.get_weights()
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                if not self.__weights[i][j] == other_weights[i][j]:
                    return False
        return self.__weights[self.__columns - 1][0] == other_weights[self.__columns - 1][0]
    
    # Finds the gradient of the neural net at the value x by the weight vector for the i, j node
    def gradient(self, x, i, j):
        return [self.__output_node.derivative(x, i, j, k) for k in range(len(self.__weights[i][j]))]

    def generate_weights(self):
        self.__weights = [[[] for j in range(self.__rows)] for i in range(self.__columns - 1)]
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                num_weights = self.__rows
                if i == 0:
                    num_weights = 1
                self.__weights[i][j] = np.random.uniform(0, 1, num_weights).tolist()
        self.__weights.append([np.random.uniform(0, 1, self.__rows).tolist()])

        return

    def get_size(self):
        return self.__columns, self.__rows

    def get_weights(self):
        return self.__weights

    def print_weights(self):
        for i in range(self.__columns - 1):
            for j in range(self.__rows):
                print("Node " + str(i) + ", " + str(j) + " weights: " + str(self.__weights[i][j]))
        print("Node " + str(self.__columns - 1) + ", " + str(0) + " weights: "
              + str(self.__weights[self.__columns - 1][0]))
        return

    def save_net(self, file_name):
        with open(file_name, "w") as net_file:
            net_data = {"columns": self.__columns, "rows": self.__rows,
                        "weights": self.__weights}
            json.dump(net_data, net_file)
        return

    def set_node_weights(self, i, j, new_weights):
        self.__nodes[i][j].set_weights(new_weights)
        return
