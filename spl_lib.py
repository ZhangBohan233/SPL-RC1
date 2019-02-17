import time as time_lib
import spl_interpreter as inter
import spl_lexer as lex
import spl_parser as psr


class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get(self):
        return self.count


def replace_bool_none(string):
    in_single = False
    in_double = False
    lst = []
    i = 0
    while i < len(string):
        ch = string[i]
        if in_single:
            if ch == "'":
                in_single = False
        elif in_double:
            if ch == '"':
                in_double = False
        else:
            if ch == "'":
                in_single = True
            elif ch == '"':
                in_double = True
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


DEBUG = False

ID_COUNTER = Counter()


class Environment:
    """
    ===== Attributes =====
    :type is_global: bool
    :type heap: dict
    :type variables: dict
    :type privates: set
    :type outer: Environment
    :type temp_vars: list
    """

    def __init__(self, is_global, heap):
        self.is_global = is_global
        self.heap = heap  # Heap-allocated variables (global)
        self.variables = {}  # Stack variables
        self.privates = set()
        self.outer = None  # Outer environment, only used for inner functions
        self.temp_vars = []

        self.scope_name = None

        # environment signals
        self.terminated = False
        self.exit_value = None
        self.broken = False
        self.paused = False

        if is_global:
            self._add_natives()
            # self._add_base_exception()

    def __str__(self):
        if self.scope_name:
            return self.scope_name
        else:
            return str(super)

    def _add_natives(self):
        self.add_heap("print", NativeFunction(print_, "print"))
        self.add_heap("type", NativeFunction(typeof, "type"))
        self.add_heap("pair", NativeFunction(make_pair, "pair"))
        self.add_heap("list", NativeFunction(make_list, "list"))
        self.add_heap("set", NativeFunction(make_set, "set"))
        self.add_heap("int", NativeFunction(to_int, "int"))
        self.add_heap("float", NativeFunction(to_float, "float"))
        self.add_heap("string", NativeFunction(to_str, "string"))
        self.add_heap("input", NativeFunction(input_, "input"))
        self.add_heap("f_open", NativeFunction(f_open, "f_open"))
        self.add_heap("eval", NativeFunction(eval_, "eval"))
        self.add_heap("dir", NativeFunction(dir_, "dir", self))

        self.add_heap("boolean", NativeFunction(to_boolean, "boolean"))
        self.add_heap("void", NativeFunction(None, "void"))

    def add_heap(self, k, v):
        self.heap[k] = v

    def terminate(self, exit_value):
        self.terminated = True
        self.broken = True
        self.exit_value = exit_value

    def break_loop(self):
        self.broken = True

    def pause_loop(self):
        self.paused = True

    def assign(self, key, value):
        if self.is_global:
            self.heap[key] = value
        elif key in self.variables:
            self.variables[key] = value
        else:
            # look for outer first
            out = self.outer
            found = False
            while out:
                if key in out.variables:
                    out.variables[key] = value
                    found = True
                    break
                out = out.outer
            if not found:
                self.variables[key] = value

    def add_private(self, key):
        if key in self.variables:
            self.privates.add(key)
        else:
            # look for outer first
            out = self.outer
            found = False
            while out:
                if key in out.variables:
                    out.privates.add(key)
                    found = True
                    break
                out = out.outer
            if not found:
                self.privates.add(key)

    def inner_get(self, key: str):
        if key in self.variables:
            return self.variables[key]
        elif self.outer:
            return self.outer.inner_get(key)
        else:
            if key in self.heap:
                return self.heap[key]
            else:
                return NULLPTR

    def is_private(self, key):
        if key in self.privates:
            return True
        elif self.outer:
            return self.outer.is_private(key)
        else:
            return False

    def get(self, key: str, line_file: tuple):
        """
        Returns the value of that key.

        :param key:
        :param line_file:
        :return:
        """
        v = self.inner_get(key)
        if v == NULLPTR:
            raise SplException("Usage before assignment for name '{}', in file {}, at line {}"
                               .format(key, line_file[1], line_file[0]))
        else:
            return v

    def contains_key(self, key: str):
        v = self.inner_get(key)
        if v == NULLPTR:
            return False
        else:
            return True

    def get_class(self, class_name):
        return self.heap[class_name]


class NativeFunction:
    def __init__(self, func: callable, name: str, env: Environment = None):
        self.name = name
        self.function = func
        self.parent_env: Environment = env

    def __str__(self):
        return "NativeFunction {}".format(self.function.__name__)

    def __repr__(self):
        return self.__str__()

    def call(self, args):
        if self.parent_env:
            return self.function(self.parent_env, *args)
        else:
            return self.function(*args)


class Function:
    """
    :type body: BlockStmt
    :type outer_scope: Environment
    """

    def __init__(self, params, presets, body):
        # self.name = f_name
        self.params: list = params
        self.presets: list = presets
        self.body = body
        self.outer_scope = None

    def __str__(self):
        return "Function<{}>".format(id(self))

    def __repr__(self):
        return self.__str__()


class Class:
    def __init__(self, class_name: str, body: psr.BlockStmt):
        self.class_name = class_name
        self.body = body
        self.superclass_names = []

    def __str__(self):
        if len(self.superclass_names):
            return "Class<{}> extends {}".format(self.class_name, self.superclass_names)
        else:
            return "Class<{}>".format(self.class_name)

    def __repr__(self):
        return self.__str__()


# class Primitive:
#     def __init__(self):
#         pass
#
#     def type_name(self):
#         raise NotImplementedError
#
#
# class Null(Primitive):
#     def __init__(self):
#         Primitive.__init__(self)
#
#     def __eq__(self, other):
#         return isinstance(other, Null)
#
#     def __bool__(self):
#         return False
#
#     def __str__(self):
#         return "null"
#
#     def __repr__(self):
#         return self.__str__()
#
#     def type_name(self):
#         return "void"
#
#
# class Boolean(Primitive):
#     def __init__(self, value: bool):
#         Primitive.__init__(self)
#         self.value = value
#
#     def __eq__(self, other):
#         return isinstance(other, Boolean) and self.value == other.value
#
#     def __neg__(self):
#         return FALSE if self.value else TRUE
#
#     def __bool__(self):
#         return self.value
#
#     def __str__(self):
#         return "true" if self.value else "false"
#
#     def __repr__(self):
#         return self.__str__()
#
#     def type_name(self):
#         return "boolean"


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


class Iterable:
    def __init__(self):
        pass

    def __iter__(self):
        raise NotImplementedError


class String(NativeType, Iterable):
    def __init__(self, lit):
        NativeType.__init__(self)

        self.literal: str = lit

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
            raise TypeException("Cannot add <string> with {}".format(typeof(other)))

    def __getitem__(self, index):
        return self.literal[index]

    def contains(self, char):
        return char in self.literal

    def type_name(self):
        return "string"


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


# Native functions

def print_(*args):
    # print(type(args[0]))
    a0 = args[0]
    s = replace_bool_none(str(a0))
    print(s, *args[1:])
    # print(*args)
    return None


def input_(*prompt):
    s = input(*prompt)
    return String(s)


def typeof(obj):
    if obj is None:
        return "void"
    elif isinstance(obj, inter.ClassInstance):
        return String(obj.class_name)
    elif isinstance(obj, bool):
        return String("boolean")
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
    return True if v else False


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


def dir_(env, obj):
    lst = List()
    if isinstance(obj, inter.Class):
        # instance = inter.ClassInstance(env, obj.class_name)
        create = psr.ClassInit((0, "dir"), obj.class_name)
        instance = inter.evaluate(create, env)
        exc = {"id", "this"}
        for attr in instance.env.variables:
            if attr not in exc:
                lst.append(attr)
    elif isinstance(obj, inter.NativeFunction):
        for nt in NativeType.__subclasses__():
            if nt.type_name(nt) == obj.name:
                lst.extend(dir(nt))
    elif isinstance(obj, NativeType):
        for nt in NativeType.__subclasses__():
            if nt.type_name(nt) == obj.type_name():
                lst.extend(dir(nt))
    lst.sort()
    return lst


# Exceptions

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


# NULL = Null()
# TRUE = Boolean(True)
# FALSE = Boolean(False)
NULLPTR = NullPointer()

PRIMITIVE_FUNC_TABLE = {
    "boolean": "bool",
    "void": "NoneType"
}
