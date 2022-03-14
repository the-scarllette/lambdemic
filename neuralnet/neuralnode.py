def ramp(x):
    if x <= 0:
        return 0
    return x


def ramp_derivative(x):
    if x <= 0:
        return 0
    return 1


class NeuralNode:
    activation_functions = {'ramp': {'function': ramp, 'derivative': ramp_derivative}}

    def __init__(self, weights, i, j, input_nodes, input_node, activation_function='ramp'):
        self.__i = i
        self.__j = j
        self.__weights = weights
        self.__is_input_node = input_node
        if self.__is_input_node:
            self.__input_nodes = None
        else:
            self.__input_nodes = input_nodes
        self.__activation_function = NeuralNode.activation_functions[activation_function]['function']
        self.__act_func_derivative = NeuralNode.activation_functions[activation_function]['derivative']
        self.__num_inputs = len(self.__weights)
        return

    def adjust_weights(self, adjust_amount):
        for i in range(self.__num_inputs):
            self.__weights[i] += adjust_amount[i]
        return

    def compute(self, inputs):
        try:
            inputs[0]
        except TypeError:
            inputs = [inputs]
        return self.__activation_function(sum([self.__weights[i] * inputs[i] for i in range(self.__num_inputs)]))

    def compute_recursive(self, inputs):
        if self.__is_input_node:
            return self.__activation_function(self.__weights[0] * inputs[self.__j])
        return self.__activation_function(sum([self.__weights[i] * self.__input_nodes[i].compute_recursive(inputs)
                                               for i in range(self.__num_inputs)]))

    # Finds the partial derivative of the node at the point x w.r.t the kth weight of the i, j node
    def derivative(self, x, i, j, k):
        if self.__i == i and self.__j == j:
            return self.derivative_self_weights(x, i, j, k)  # If the weight belongs to this node
        return self.derivative_other_weights(x, i, j, k)  # If the weight is of a different node

    def derivative_other_weights(self, x, i, j, k):
        if self.__is_input_node:
            return 0
        derivative_sum = sum([self.__weights[l]*self.__input_nodes[l].derivative(x, i, j, k)
                              for l in range(self.__num_inputs)])
        node_sum = sum([self.__weights[l]*self.__input_nodes[l].compute_recursive(x)
                        for l in range(self.__num_inputs)])
        return derivative_sum*self.__act_func_derivative(node_sum)

    def derivative_self_weights(self, x, i, j, k):
        if self.__is_input_node:
            return x[j]*self.__act_func_derivative(self.__weights[0]*x[j])
        node_sum = sum([self.__weights[l]*self.__input_nodes[l].compute_recursive(x)
                        for l in range(self.__num_inputs)])
        return self.__input_nodes[k].compute_recursive(x)*self.__act_func_derivative(node_sum)

    def set_weights(self, new_weights):
        self.__weights = new_weights
        return
