import sys
import time as time_lib


def replace_bool_none(string: str):
    """
    Returns a str with 'None', 'True', and 'False' replaced with 'null', 'true', and 'false'.

    This function also removes quotes generated by spl String object.

    :param string: the str object to be replaced
    :return: a str with 'None', 'True', and 'False' replaced with 'null', 'true', and 'false'
    """
    in_single = False
    in_double = False
    lst = []
    i = 0
    while i < len(string):
        ch = string[i]
        if in_single:
            if ch == "'":
                in_single = False
                i += 1
                continue
        elif in_double:
            if ch == '"':
                in_double = False
                i += 1
                continue
        else:
            if ch == "'":
                in_single = True
                i += 1
                continue
            elif ch == '"':
                in_double = True
                i += 1
                continue
        if not in_single and not in_double:
            if i <= len(string) - 4:
                if string[i:i + 4] == "True":
                    lst.append("true")
                    i += 4
                    continue
                elif string[i:i + 4] == "None":
                    lst.append("null")
                    i += 4
                    continue
            if i <= len(string) - 5:
                if string[i:i + 5] == "False":
                    lst.append("false")
                    i += 5
                    continue
        lst.append(ch)
        i += 1
    return "".join(lst)


def print_waring(msg: str):
    sys.stderr.write(msg + "\n")


# Native functions with no dependency


class NativeType:
    def __init__(self):
        pass

    def type_name(self) -> str:
        raise NotImplementedError


class Iterable:
    def __init__(self):
        pass

    def __iter__(self):
        raise NotImplementedError


class String(NativeType, Iterable):
    def __init__(self, lit):
        NativeType.__init__(self)

        if isinstance(lit, String):
            self.literal = lit.literal
        else:
            self.literal: str = str(lit)

    def __iter__(self):
        return (c for c in self.literal)

    def __str__(self):
        return "'" + self.literal + "'"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, String) and self.literal == other.literal

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, String):
            return String(self.literal + other.literal)
        else:
            raise TypeException("Cannot add <string> with <{}>".format(type(other).__name__))

    def __getitem__(self, index):
        return self.literal[index]

    def length(self):
        return len(self.literal)

    def text(self):
        return self.literal

    def contains(self, char):
        return char in self.literal

    def type_name(self):
        return "string"

    # def join(self, iterable):
    #     raise NotImplementedError


class List(NativeType, Iterable):
    def __init__(self, *initial):
        NativeType.__init__(self)

        self.list = [*initial]

    def __iter__(self):
        return (x for x in self.list)

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

    def pop(self, index=-1):
        return self.list.pop(index)

    def clear(self):
        return self.list.clear()

    def extend(self, lst):
        self.list.extend(lst)

    def length(self):
        return len(self.list)

    def sort(self):
        self.list.sort()

    def reverse(self):
        self.list.reverse()


class Pair(NativeType, Iterable):
    def __init__(self):
        NativeType.__init__(self)

        self.pair = {}

    def __iter__(self):
        return (k for k in self.pair)

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


class Set(NativeType, Iterable):
    def __init__(self):
        NativeType.__init__(self)

        self.set = set()

    def __iter__(self):
        return (v for v in self.set)

    def __str__(self):
        return str(self.set)

    def __repr__(self):
        return self.__str__()

    def size(self):
        return len(self.set)

    def add(self, item):
        self.set.add(item)

    def pop(self):
        self.set.pop()

    def clear(self):
        self.set.clear()

    def union(self, other):
        self.set.union(other)

    def update(self, s):
        self.set.update(s)

    def contains(self, item):
        return item in self.set

    def type_name(self):
        return "set"


class System(NativeType):
    argv: List
    encoding: str
    stdout = sys.stdout
    stderr = sys.stderr

    def __init__(self, argv_: List, enc: str):
        NativeType.__init__(self)

        type(self).argv = argv_
        type(self).encoding = enc

    def time(self):
        return int(time_lib.time() * 1000)

    def type_name(self):
        return "system"


class File(NativeType):
    """
    :type fp:
    """

    def __init__(self, fp, mode):
        NativeType.__init__(self)

        self.mode = mode
        self.fp = fp

    def read_one(self):
        r = self.fp.read(1)
        if r:
            if self.mode == "r":
                return String(r)
            elif self.mode == "rb":
                return int(self.fp.read(1)[0])
            else:
                raise IOException("Wrong mode")
        else:
            return None

    def read(self):
        if self.mode == "r":
            return String(self.fp.read())
        elif self.mode == "rb":
            return List(*list(self.fp.read()))
        else:
            raise IOException("Wrong mode")

    def readline(self):
        if self.mode == "r":
            s = self.fp.readline()
            if s:
                return String(s)
            else:
                return None
        else:
            raise IOException("Wrong mode")

    def write(self, s):
        if "w" in self.mode:
            if "b" in self.mode:
                self.fp.write(bytes(s))
            else:
                self.fp.write(str(s))
            return None
        else:
            raise IOException("Wrong mode")

    def flush(self):
        if "w" in self.mode:
            self.fp.flush()
            return None
        else:
            raise IOException("Wrong mode")

    def close(self):
        self.fp.close()
        return None

    def type_name(self):
        return "file"


# Exceptions

class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


class SplException(InterpretException):
    def __init__(self, msg=""):
        InterpretException.__init__(self, msg)


class TypeException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class IndexOutOfRangeException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class IOException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class AbstractMethodException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class UnauthorizedException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class ArgumentException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


class ArithmeticException(SplException):
    def __init__(self, msg=""):
        SplException.__init__(self, msg)


def print_ln(*args):
    if len(args) > 0:
        print_(*args)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return None


def print_(*args):
    a0 = args[0]
    if len(args) == 1:
        stream = sys.stdout
    else:
        stream = args[1]
    s = replace_bool_none(str(a0))
    stream.write(s)
    return None


def exit_(code=0):
    exit(code)


def input_(*prompt):
    s = input(*prompt)
    return String(s)


def make_list(*initial_elements):
    lst = List(*initial_elements)
    return lst


def make_pair():
    pair = Pair()
    return pair


def make_set():
    s = Set()
    return s


def to_int(v):
    return int(v)


def to_float(v):
    return float(v)


def to_boolean(v):
    return True if v else False


def f_open(file, mode=String("r"), encoding=String("utf-8")):
    if not mode.contains("b"):
        f = open(str(file), str(mode), encoding=str(encoding))
    else:
        f = open(str(file), str(mode))
    return File(f, str(mode))


# etc


class InvalidArgument:
    def __init__(self):
        pass
