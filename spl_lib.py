import time as time_lib
import spl_interpreter as inter
import spl_lexer as lex


class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get(self):
        return self.count


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

    def __neg__(self):
        return FALSE if self.value else TRUE

    def __bool__(self):
        return self.value

    def __str__(self):
        return "true" if self.value else "false"

    def __repr__(self):
        return self.__str__()

    def type_name(self):
        return "boolean"


class NullPointer:
    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, NullPointer)


class NativeType:
    def __init__(self):
        pass

    def type_name(self):
        raise NotImplementedError


class String(NativeType):
    def __init__(self, lit):
        NativeType.__init__(self)

        self.literal: str = lit

    def __str__(self):
        return self.literal

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return TRUE if isinstance(other, String) and self.literal == other.literal else FALSE

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        if isinstance(other, String):
            return String(self.literal + other.literal)
        else:
            raise TypeException("Cannot add <string> with {}".format(typeof(other)))

    def __getitem__(self, index):
        return self.literal[index]

    def contains(self, char):
        return TRUE if char in self.literal else FALSE

    def type_name(self):
        return "string"


class List(NativeType):
    def __init__(self, *initial):
        NativeType.__init__(self)

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
        return TRUE if item in self.list else FALSE

    def insert(self, index, item):
        self.list.insert(index, item)

    def pop(self, index):
        return self.list.pop(index)

    def clear(self):
        return self.list.clear()

    def length(self):
        return len(self.list)


class Pair(NativeType):
    def __init__(self):
        NativeType.__init__(self)

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
        return TRUE if item in self.pair else FALSE

    def size(self):
        return len(self.pair)

    def type_name(self):
        return "pair"


class Set(NativeType):
    def __init__(self):
        NativeType.__init__(self)

        self.set = set()

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
        return TRUE if item in self.set else FALSE

    def type_name(self):
        return "set"


class System(NativeType):
    argv = None
    encoding = None

    def __init__(self, argv_: list, enc: str):
        NativeType.__init__(self)

        type(self).argv = argv_
        setattr(self, "encoding", enc)

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
            return NULL

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
                return NULL
        else:
            raise IOException("Wrong mode")

    def write(self, s):
        if "w" in self.mode:
            if "b" in self.mode:
                self.fp.write(bytes(s))
            else:
                self.fp.write(str(s))
            return NULL
        else:
            raise IOException("Wrong mode")

    def flush(self):
        if "w" in self.mode:
            self.fp.flush()
            return NULL
        else:
            raise IOException("Wrong mode")

    def close(self):
        self.fp.close()
        return NULL

    def type_name(self):
        return "file"


def print_(*args):
    print(*args)
    return NULL


def input_(*prompt):
    s = input(*prompt)
    return String(s)


def typeof(obj):
    if isinstance(obj, inter.ClassInstance):
        return String(obj.class_name)
    elif isinstance(obj, Primitive):
        return String(obj.type_name())
    elif isinstance(obj, NativeType):
        return String(obj.type_name())
    else:
        t = type(obj)
        return String(t.__name__)


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


def to_str(v):
    return String(str(v))


def to_boolean(v):
    return TRUE if v else FALSE


def f_open(file, mode=String("r"), encoding=String("utf-8")):
    if not mode.contains("b"):
        f = open(str(file), str(mode), encoding=str(encoding))
    else:
        f = open(str(file), str(mode))
    return File(f, str(mode))


def eval_(expr):
    lexer = lex.Lexer()
    lexer.file_name = "expression"
    lexer.script_dir = "expression"
    lexer.tokenize([str(expr)])
    block = lexer.parse()
    return block


class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


class SplException(InterpretException):
    def __init__(self, msg=""):
        InterpretException.__init__(self, msg)


class TypeException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)


class IndexOutOfRangeException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)


class IOException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)


class AbstractMethodException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)


class UnauthorizedException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)
NULLPTR = NullPointer()
