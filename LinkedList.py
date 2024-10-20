class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self, list1=None):
        if list1:
            self.head = Node(list1[0])
            last_node = self.head
            for element in list1[1:]:
                node = Node(element)
                last_node.next = node
                last_node = node
            self.flag = False
        else:
            self.head = None

    def insert_list(self, list1):
        first = self.head
        for l in list1:
            node = Node(l)
            node.next = first
            first = node
        self.head = first

    # method to add a node in the beginning
    def insertAtBegin(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    # method to run over the
    def run_over(self):
        node = self.head
        while node is not None:
            yield node.data
            node = node.next
