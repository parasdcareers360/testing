
class Node:
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next



class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        node = Node(data)

        if self.head == None:
            self.head = node
            return

        current = self.head

        while current.next is not None:
            current = current.next

        current.next = node

    def display(self):
        current = self.head

        while current.next is not None:
            

        