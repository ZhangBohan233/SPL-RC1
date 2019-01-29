class Map:
    def __init__(self):
        pass

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class HashMap(Map):
    def __init__(self):
        Map.__init__(self)

        self.d = {}

    def __str__(self):
        return str(self.d)

    def __len__(self):
        return len(self.d)

    def __setitem__(self, key, value):
        self.d[key] = value

    def __getitem__(self, item):
        return self.d[item]

    def __contains__(self, item):
        return item in self.d

    def merge(self, other):
        for key in other.d:
            self.d[key] = other.d[key]


class Stack:
    """
    :type head: StackNode
    """
    def __init__(self):
        self.head = None

    def add(self, v):
        node = StackNode(v)
        node.after = self.head
        self.head = node

    def pop(self):
        node = self.head
        self.head = node.after
        return node.value

    def top(self):
        return self.head.value

    def empty(self):
        return self.head is None


class StackNode:
    def __init__(self, value):
        self.value = value
        self.after = None
