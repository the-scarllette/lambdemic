from neuralnet import ramp


class NeuralNode:

    def __init__(self, weights, input_nodes, input_node, activation_function):
        self.__weights = weights
        self.__is_input_node = input_node
        if self.__is_input_node:
            self.__input_nodes = None
        else:
            self.__input_nodes = input_nodes
        self.__activation_function = activation_function
        self.__num_inputs = len(self.__input_nodes)
        return

    def compute(self, inputs):
        try:
            inputs[0]
        except TypeError:
            inputs = [inputs]
        return self.__activation_function(sum([self.__weights[i]*inputs[i] for i in range(self.__num_inputs)]))
