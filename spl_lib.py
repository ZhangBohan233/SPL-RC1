import time as time_lib
import spl_interpreter as inter


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


class StackNode:
    def __init__(self, value):
        self.value = value
        self.after = None


class Primitive:
    def __init__(self):
        pass

    def type_name(self):
        raise NotImplementedError


class Null(Primitive):
    def __init__(self):
        Primitive.__init__(self)

    def __eq__(self, other):
        return isinstance(other, Null)

    def __bool__(self):
        return False

    def __str__(self):
        return "null"

    def __repr__(self):
        return self.__str__()

    def type_name(self):
        return "void"


class Boolean(Primitive):
    def __init__(self, value: bool):
        Primitive.__init__(self)
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Boolean) and self.value == other.value

    def __bool__(self):
        return self.value

    def __str__(self):
        return "true" if self.value else "false"

    def __repr__(self):
        return self.__str__()

    def type_name(self):
        return "boolean"


class NativeTypes:
    def __init__(self):
        pass

    def type_name(self):
        raise NotImplementedError


class String(NativeTypes):
    def __init__(self, lit):
        NativeTypes.__init__(self)

        self.literal = lit

    def __str__(self):
        return self.literal

    def __repr__(self):
        return self.literal

    def __getitem__(self, index):
        return self.literal[index]

    def type_name(self):
        return "string"


class List(NativeTypes):
    def __init__(self, *initial):
        NativeTypes.__init__(self)

        self.list = [*initial]

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.list[item]

    def __setitem__(self, key, value):
        self.list[key] = value

    def set(self, key, value):
        self.__setitem__(key, value)

    def get(self, key):
        self.__getitem__(key)

    def type_name(self):
        return "list"

    def append(self, value):
        self.list.append(value)

    def contains(self, item):
        return item in self.list

    def insert(self, index, item):
        self.list.insert(index, item)

    def pop(self, index):
        return self.list.pop(index)

    def clear(self):
        return self.list.clear()

    def length(self):
        return len(self.list)


class Pair(NativeTypes):
    def __init__(self):
        NativeTypes.__init__(self)

        self.pair = {}

    def __str__(self):
        return str(self.pair)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.pair[item]

    def __setitem__(self, key, value):
        self.pair[key] = value

    def contains(self, item):
        return item in self.pair

    def size(self):
        return len(self.pair)

    def type_name(self):
        return "pair"


class System(NativeTypes):
    argv = None

    def __init__(self, argv_: list):
        NativeTypes.__init__(self)

        type(self).argv = argv_

    def type_name(self):
        return "system"


def print_(*args):
    print(*args)
    return NULL


def time():
    return int(time_lib.time() * 1000)


def typeof(obj):
    if isinstance(obj, inter.ClassInstance):
        return obj.classname
    elif isinstance(obj, Primitive):
        return obj.type_name()
    elif isinstance(obj, NativeTypes):
        return obj.type_name()
    else:
        t = type(obj)
        return t.__name__


def make_list(*initial_elements):
    lst = List(*initial_elements)
    return lst


def make_pair():
    pair = Pair()
    return pair


def to_int(v):
    return int(v)


def to_float(v):
    return float(v)


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)
