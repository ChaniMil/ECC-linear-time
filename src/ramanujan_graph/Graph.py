import numpy as np


class Graph:
    def __init__(self, num_of_nodes, degree):
        """
        initialization of the graph object
        :param num_of_nodes: an upper bound of the number of nodes
        :param degree: the degree of each node in the graph
        """
        self.degree = degree
        self.num_of_nodes = num_of_nodes
        self.neighbors = np.zeros((num_of_nodes, degree), dtype=int)

        self.num_of_neighbors = [0] * num_of_nodes
        self.is_left = [False] * num_of_nodes

        nodes_on_each_side = num_of_nodes // 2
        self.A = [-1] * nodes_on_each_side
        self.B = [-1] * nodes_on_each_side
        self.sets = self.A, self.B
        self.num_of_edges = nodes_on_each_side * degree

    def add_edge(self, a, b, qr):
        """
        this function add an edge to the graph between the two nodes
        :param a: first node
        :param b: second node
        :param qr: the side of the first node
        :return: None
        """
        # adding only for 'a' because this function will be called again where a and b are swapped
        self.neighbors[a][self.num_of_neighbors[a]] = b  # setting b as a neighbor of a
        self.neighbors[b][self.num_of_neighbors[b]] = a  # setting b as a neighbor of a
        self.num_of_neighbors[a] += 1  # increase the counter
        self.num_of_neighbors[b] += 1  # increase the counter
        self.is_left[a] = qr
        self.is_left[a] = not qr

    def split_to_sides(self):
        """
        this function splits the nodes to 2 sides A,B
        :return: None
        """
        total_counter = 0  # counter_A + counter_B
        counter_A = counter_B = 0  # the number of nodes in each of the sides
        while total_counter < self.num_of_nodes:  # if there are nodes
            if self.is_left[total_counter]:  # check if the current node is on the left side
                self.A[counter_A] = total_counter  # set the next node of A in the next location
                counter_A += 1  # update the number of nodes in A
            else:
                self.B[counter_B] = total_counter  # set the next node of B in the next location
                counter_B += 1  # update the number of nodes in B
            total_counter += 1  # to the next node
        self.sets = self.A, self.B

    def edges(self):
        """
        this function collects all the edges of the graph
        :return: list of all the edges
        """
        # the edges are all the left side and its neighbors
        return [[i, self.neighbors[i][j]] for j in range(self.degree) for i in self.A]
