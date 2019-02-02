import time as time_lib
import spl_interpreter as inter

TYPE_NAMES = {"Null": "void", "Boolean": "boolean", "List": "list"}


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

    def clear(self):
        self.d.clear()

    def key_set(self):
        return set(self.d.keys())

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


class Null:
    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, Null)

    def __str__(self):
        return "null"

    def __repr__(self):
        return self.__str__()


class Boolean:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Boolean) and self.value == other.value

    def __str__(self):
        return "true" if self.value else "false"

    def __repr__(self):
        return self.__str__()


class NativeTypes:
    def __init__(self):
        pass


class List(NativeTypes):
    def __init__(self, *initial):
        NativeTypes.__init__(self)

        self.list = [*initial]

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return self.__str__()

    def append(self, value):
        self.list.append(value)


class StackNode:
    def __init__(self, value):
        self.value = value
        self.after = None


def time():
    return int(time_lib.time() * 1000)


def typeof(obj):
    if isinstance(obj, inter.ClassInstance):
        return obj.classname
    else:
        t = type(obj)
        if t.__name__ in TYPE_NAMES:
            return TYPE_NAMES[t.__name__]
        else:
            return t


def make_list(*initial_elements):
    lst = List(*initial_elements)
    return lst
