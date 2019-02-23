import spl_parser as psr
import spl_lexer as lex
import time as time_lib
from spl_lexer import BINARY_OPERATORS

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]


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
        self.constants = {}
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
        temp = [self.scope_name, "\nConst: "]
        for c in self.constants:
            if c != "this":
                temp.append(str(c))
                temp.append(": ")
                temp.append(str(self.constants[c]))
                temp.append(", ")
        temp.append("\nVars: ")
        for v in self.variables:
            temp.append(str(v))
            temp.append(": ")
            temp.append(str(self.variables[v]))
            temp.append(", ")
        temp.append("\nHeap: ")
        for hv in self.heap:
            temp.append(str(hv))
            temp.append(": ")
            temp.append(str(self.heap[hv]))
            temp.append(", ")
        return "".join(temp)

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
        # if self.is_global:
        #     self.heap[key] = value
        if key in self.constants:
            raise SplException("Re-assignment to constant values.")
        elif key in self.variables:
            self.variables[key] = value
        else:
            # look for outer first
            out = self.outer
            while out:
                if key in out.constants:
                    raise SplException("Re-assignment to constant values.")
                if key in out.variables:
                    out.variables[key] = value
                    return
                out = out.outer
            self.variables[key] = value

    def assign_const(self, key, value):
        if key in self.constants:
            raise SplException("Attempt to change a constant value")
        else:
            self.constants[key] = value

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
        if key in self.constants:
            return self.constants[key]
        elif key in self.variables:
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

    def get(self, key: str, line_file):
        """
        Returns the value of that key.

        :param key:
        :param line_file:
        :return:
        """
        v = self.inner_get(key)
        if v == NULLPTR:
            raise SplException("Name '{}' is not defined, in file {}, at line {}"
                               .format(key, line_file[1], line_file[0]))
        else:
            return v

    def direct_get(self, key: str):
        if key in self.constants:
            return self.constants[key]
        else:
            return self.variables[key]

    def contains_key(self, key: str):
        v = self.inner_get(key)
        if v == NULLPTR:
            return False
        else:
            return True

    def get_heap(self, class_name):
        return self.heap[class_name]

    def attributes(self):
        return {**self.constants, **self.variables}


class NativeFunction:
    def __init__(self, func: callable, name: str, env: Environment = None):
        self.name = name
        self.function = func
        self.parent_env: Environment = env

    def __str__(self):
        try:
            return "NativeFunction {}".format(self.function.__name__)
        except AttributeError:
            return ""

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
    length = 0

    def __init__(self, lit):
        NativeType.__init__(self)

        self.literal: str = lit
        self.length = len(lit)

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

    def text(self):
        return self.literal

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
    elif isinstance(obj, ClassInstance):
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


def eval_(expr: String):
    lexer = lex.Lexer()
    lexer.file_name = "expression"
    lexer.script_dir = "expression"
    lexer.tokenize([expr.text()])
    block = lexer.parse()
    return block


def dir_(env, obj):
    lst = List()
    if isinstance(obj, Class):
        # instance = inter.ClassInstance(env, obj.class_name)
        create = psr.ClassInit((0, "dir"), obj.class_name)
        instance: ClassInstance = evaluate(create, env)
        exc = {"id", "this"}
        # for attr in instance.env.variables:
        for attr in instance.env.attributes():
            if attr not in exc:
                lst.append(attr)
    elif isinstance(obj, NativeFunction):
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


NULLPTR = NullPointer()

PRIMITIVE_FUNC_TABLE = {
    "boolean": "bool",
    "void": "NoneType"
}


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    :type encoding: str
    """

    def __init__(self, argv, encoding):
        self.ast = None
        self.argv = argv
        self.env = Environment(True, {})
        self.env.add_heap("system", System(argv, encoding))
        self.env.scope_name = "Global"

    def set_ast(self, ast: psr.BlockStmt):
        """
        Sets up the abstract syntax tree to be interpreted.

        :param ast: the root of the abstract syntax tree to be interpreted
        :return: None
        """
        self.ast = ast

    def interpret(self):
        """
        Starts the interpretation.

        :return: the exit value
        """
        return evaluate(self.ast, self.env)


class Module:
    def __init__(self, mod_name: str, env: Environment):
        self.module_name = mod_name
        self.env = env

    def __str__(self):
        return "Module '{}': {}".format(self.module_name, self.env.attributes())


class ClassInstance:
    """
    ===== Attributes =====
    :param class_name: name of this class
    :param env: instance attributes
    """

    def __init__(self, env: Environment, class_name: str):
        self.class_name = class_name
        self.env = env
        self.env.constants["id"] = ID_COUNTER.get()
        ID_COUNTER.increment()
        self.env.constants["this"] = self

    def __hash__(self):
        if self.env.contains_key("__hash__"):
            call = psr.FuncCall((0, "interpreter"), "__hash__")
            call.args = []
            return evaluate(call, self.env)
        else:
            return hash(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.env.contains_key("__str__"):
            call = psr.FuncCall((0, "interpreter"), "__str__")
            call.args = []
            return str(evaluate(call, self.env))
        else:
            attr = self.env.attributes()
            attr.pop("this")
            return str(self.class_name) + ": " + str(attr)


class RuntimeException(Exception):
    def __init__(self, exception: ClassInstance):
        Exception.__init__(self, "RuntimeException")

        self.exception = exception


def eval_for_loop(node: psr.ForLoopStmt, env: Environment):
    con: psr.BlockStmt = node.condition
    start = con.lines[0]
    end = con.lines[1]
    step = con.lines[2]
    result = evaluate(start, env)
    while not env.broken and evaluate(end, env):
        result = evaluate(node.body, env)
        env.paused = False
        evaluate(step, env)
    env.broken = False
    return result


def eval_for_each_loop(node: psr.ForLoopStmt, env: Environment):
    con: psr.BlockStmt = node.condition
    invariant = con.lines[0].name
    target = con.lines[1]
    iterable = evaluate(target, env)
    if isinstance(iterable, Iterable):
        result = None
        for x in iterable:
            env.assign(invariant, x)
            result = evaluate(node.body, env)
            env.paused = False
            if env.broken:
                break
        env.broken = False
        return result
    elif isinstance(iterable, ClassInstance) and is_subclass_of(env.get_heap(iterable.class_name), "Iterable",
                                                                env):
        lf = (0, "interpreter")
        ite = psr.FuncCall(lf, "__iter__")
        iterator: ClassInstance = evaluate(ite, iterable.env)
        result = None
        while not env.broken:
            nex = psr.FuncCall(lf, "__next__")
            res = evaluate(nex, iterator.env)
            if isinstance(res, ClassInstance) and is_subclass_of(env.get_heap(res.class_name), "StopIteration",
                                                                 env):
                break
            env.assign(invariant, res)
            result = evaluate(node.body, env)
            env.paused = False
        env.broken = False
        return result
    else:
        raise SplException(
            "For-each loop on non-iterable objects, in {}, at line {}".format(node.file, node.line_num))


def eval_try_catch(node: psr.TryStmt, env: Environment):
    try:
        result = evaluate(node.try_block, env)
        env.terminated = False
        return result
    except RuntimeException as re:  # catches the exceptions thrown by SPL program
        exception: ClassInstance = re.exception
        exception_class = env.get_heap(exception.class_name)
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                if is_subclass_of(exception_class, catch_name, env):
                    result = evaluate(cat.then, env)
                    env.terminated = False
                    return result
                    # if node.finally_block is None:
                    #     return result
                    # else:
                    #     env.terminated = False
        raise re
    except Exception as e:  # catches the exceptions raised by python
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                # exception_name = exception.class_name
                if catch_name == "Exception":
                    result = evaluate(cat.then, env)
                    env.terminated = False
                    return result
        raise e
    finally:
        if node.finally_block:
            return evaluate(node.finally_block, env)


def is_subclass_of(child_class: Class, class_name: str, env: Environment) -> bool:
    """
    Returns whether the child class is the ancestor class itself or inherited from that class.

    :param child_class: the child class to be check
    :param class_name: the ancestor class
    :param env: the environment, doesn't matter whether it is global or not
    :return: whether the child class is the ancestor class itself or inherited from that class
    """
    if child_class.class_name == class_name:
        return True
    else:
        return any([is_subclass_of(env.get_heap(ccn), class_name, env) for ccn in child_class.superclass_names])


def eval_operator(node: psr.OperatorNode, env: Environment):
    left = evaluate(node.left, env)
    if node.assignment:
        right = evaluate(node.right, env)
        symbol = node.operation[:-1]
        res = arithmetic(left, right, symbol, env)
        asg = psr.AssignmentNode((node.line_num, node.file), False)
        asg.left = node.left
        asg.operation = "="
        asg.right = res
        return evaluate(asg, env)
    else:
        symbol = node.operation
        right_node = node.right
        return arithmetic(left, right_node, symbol, env)


def assignment(node: psr.AssignmentNode, env: Environment):
    key = node.left
    value = evaluate(node.right, env)
    t = key.node_type
    if t == psr.NAME_NODE:
        if node.const:
            env.assign_const(key.name, value)
        else:
            env.assign(key.name, value)
        if key.auth == lex.PRIVATE:
            env.add_private(key.name)
        return value
    elif t == psr.DOT:
        if node.const:
            raise SplException("Unsolved syntax: assigning a constant to an instance")
        node = key
        name_lst = []
        while isinstance(node, psr.Dot):
            name_lst.append(node.right.name)
            node = node.left
        name_lst.append(node.name)
        name_lst.reverse()
        # print(name_lst)
        scope = env
        for t in name_lst[:-1]:
            scope = scope.get(t, (node.line_num, node.file)).env
        scope.assign(name_lst[-1], value)
        return value
    else:
        raise InterpretException("Unknown assignment, in {}, at line {}".format(node.file, node.line_num))


def get_imported_class(namespace: psr.Namespace, env: Environment):
    return evaluate(namespace, env)


def get_module_env(node: psr.Node, env: Environment):
    if isinstance(node, psr.Namespace):
        return get_module_env(node.left, env)
    elif isinstance(node, psr.NameNode):
        return env.get_heap(node.name).env
    else:
        raise SplException("Invalid namespace in {}, at line {}".format(node.file, node.line_num))


def init_class(node: psr.ClassInit, env: Environment):
    # if isinstance(node.class_name, str):
    #     print("This should not be happened")
    #     cla: Class = env.get_heap(node.class_name)
    if node.class_name.node_type == psr.NAME_NODE:
        cla: Class = env.get_heap(node.class_name.name)
        module_env = env
    else:
        cla: Class = get_imported_class(node.class_name, env)
        module_env = get_module_env(node.class_name, env)

    # print(node)
    # print(module_env)
    scope = Environment(False, env.heap)
    scope.scope_name = "Class scope<{}>".format(cla.class_name)
    class_inheritance(cla, module_env, scope)

    # print(scope.variables)
    instance = ClassInstance(scope, node.class_name)
    for k in scope.variables:
        v = scope.variables[k]
        if isinstance(v, Function):
            # v.parent = instance
            v.outer_scope = scope

    if node.args:
        # constructor: Function = scope.variables[node.class_name]
        fc = psr.FuncCall((node.line_num, node.file), node.class_name)
        fc.args = node.args
        for a in fc.args.lines:
            scope.temp_vars.append(evaluate(a, env))
        # print(fc)
        evaluate(fc, scope)
    return instance


def get_local_function(node: psr.FuncCall, env):
    return env.get(node.f_name, (node.line_num, node.file))


def get_imported_function(node: psr.FuncCall, env: Environment):
    dot: psr.Dot = node.f_name
    res = evaluate(dot, env)
    if isinstance(res, Class):
        f = env.direct_get(res.class_name)
        return f
    else:
        return res


def call_function(node: psr.FuncCall, env: Environment):
    # print(node.f_name)
    if isinstance(node.f_name, str):
        func = get_local_function(node, env)
    else:
        func = get_imported_function(node, env)

    if isinstance(func, Function):
        scope = Environment(False, env.heap)
        scope.scope_name = "Function scope<{}>".format(node.f_name)
        scope.outer = func.outer_scope  # supports for closure

        if len(env.temp_vars) == len(func.params) > 0:
            for i in range(len(func.params)):
                scope.assign(func.params[i].name, env.temp_vars[i])
            env.temp_vars.clear()
        else:
            check_args_len(func, node)
            for i in range(len(func.params)):
                # Assign function arguments
                if i < len(node.args.lines):
                    arg = node.args.lines[i]
                else:
                    arg = func.presets[i]

                e = evaluate(arg, env)
                scope.assign(func.params[i].name, e)
        result = evaluate(func.body, scope)
        env.assign("=>", result)
        return result
    elif isinstance(func, NativeFunction):
        args = []
        for i in range(len(node.args.lines)):
            # args.append(evaluate(node.args[i], env))
            args.append(evaluate(node.args.lines[i], env))
        result = func.call(args)
        if isinstance(result, psr.BlockStmt):
            # Special case for "eval"
            res = evaluate(result, env)
            return res
        else:
            return result
    else:
        raise InterpretException("Not a function call")


def check_args_len(function: Function, call: psr.FuncCall):
    if call.args and not list(filter(lambda k: not isinstance(k, psr.InvalidToken), function.presets)).count(True) \
                         <= len(call.args.lines) <= len(function.params):
        raise SplException("Too few or too many arguments for function '{}', in '{}', at line {}"
                           .format(call.f_name, call.file, call.line_num))


def eval_namespace(node: psr.Namespace, env: Environment):
    left: Module = evaluate(node.left, env)
    obj = node.right
    t = obj.node_type
    if t == psr.NAME_NODE:
        obj: psr.NameNode
        attr = left.env.get(obj.name, (node.line_num, node.file))
        return attr
    elif t == psr.FUNCTION_CALL:
        obj: psr.FuncCall
        result = evaluate(obj, left.env)
        env.assign("=>", result)
        return result
    else:
        raise InterpretException("Unknown Syntax")


def eval_dot(node: psr.Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.node_type
    if t == psr.NAME_NODE:
        obj: psr.NameNode
        if obj.name == "this":
            raise UnauthorizedException("Access 'this' from outside")
        if isinstance(instance, NativeType):
            return native_types_invoke(instance, obj)
        elif isinstance(instance, ClassInstance):
            if (not isinstance(node.left, psr.NameNode) or node.left.name != "this") and \
                    instance.env.is_private(obj.name):
                raise UnauthorizedException("Class attribute '{}' has private access".format(obj.name))
            else:
                # attr = instance.env.variables[obj.name]
                attr = instance.env.direct_get(obj.name)
                return attr
        else:
            raise InterpretException("Neither a class instance nor a module, "
                                     "in {}, at line {}".format(node.file, node.line_num))
    elif t == psr.FUNCTION_CALL:
        obj: psr.FuncCall
        if isinstance(instance, NativeType):
            try:
                return native_types_call(instance, obj, env)
            except IndexError as ie:
                raise IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                               .format(node.file, node.line_num))
        elif isinstance(instance, ClassInstance):
            if (not isinstance(node.left, psr.NameNode) or node.left.name != "this") and \
                    instance.env.is_private(obj.f_name):
                raise UnauthorizedException("Class attribute '{}' has private access".format(obj.f_name))
            else:
                result = evaluate(obj, instance.env)
                env.assign("=>", result)
                return result
        else:
            raise InterpretException("Neither a class instance nor a module, "
                                     "in {}, at line {}".format(node.file, node.line_num))
    else:
        raise InterpretException("Unknown Syntax")


def arithmetic(left, right_node: psr.Node, symbol, env: Environment):
    if symbol in lex.LAZY:
        if left is None or isinstance(left, bool):
            return primitive_and_or(left, right_node, symbol, env)
        elif isinstance(left, int) or isinstance(left, float):
            return num_and_or(left, right_node, symbol, env)
        else:
            raise InterpretException("Operator '||' '&&' do not support type.")
    else:
        right = evaluate(right_node, env)
        if left is None or isinstance(left, bool):
            return primitive_arithmetic(left, right, symbol)
        elif isinstance(left, int) or isinstance(left, float):
            return num_arithmetic(left, right, symbol)
        elif isinstance(left, String):
            return string_arithmetic(left, right, symbol)
        elif isinstance(left, ClassInstance):
            return instance_arithmetic(left, right, symbol, env, right_node)
        else:
            return raw_type_comparison(left, right, symbol)


def instance_arithmetic(left: ClassInstance, right, symbol, env: Environment, right_node):
    if symbol == "===":
        return isinstance(right, ClassInstance) and left.env.constants["id"] == right.env.constants["id"]
    elif symbol == "!==":
        return not isinstance(right, ClassInstance) or left.env.constants["id"] != right.env.constants["id"]
    elif symbol == "instanceof":
        if isinstance(right, Class):
            return is_subclass_of(env.get_heap(left.class_name), right.class_name, env)
        elif isinstance(right_node, psr.NameNode) and isinstance(right, Function):
            right_extra = env.get_heap(right_node.name)
            return is_subclass_of(env.get_heap(left.class_name), right_extra.class_name, env)
        else:
            return False
    else:
        fc = psr.FuncCall((0, "interpreter"), "@" + BINARY_OPERATORS[symbol])
        left.env.temp_vars.append(right)
        res = evaluate(fc, left.env)
        return res


def string_arithmetic(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "+":
        result = left + right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        return isinstance(right, NativeFunction) and right.name == "string"
    else:
        raise TypeException("Unsupported operation between string and " + typeof(right))

    return result


def raw_type_comparison(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, String):
            return type(left).__name__ == right.literal
        else:
            return False
    else:
        raise InterpretException("Unsupported operation for raw type " + left.type_name())

    return result


def primitive_and_or(left, right_node: psr.Node, symbol, env: Environment):
    if left:
        if symbol == "&&":
            right = evaluate(right_node, env)
            return right
        elif symbol == "||":
            return True
        else:
            raise InterpretException("Unsupported operation for primitive type")
    else:
        if symbol == "&&":
            return False
        elif symbol == "||":
            right = evaluate(right_node, env)
            return right
        else:
            raise InterpretException("Unsupported operation for primitive type")


def primitive_arithmetic(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        return isinstance(right, NativeFunction) and PRIMITIVE_FUNC_TABLE[right.name] == type(left).__name__
    else:
        raise InterpretException("Unsupported operation for primitive type")

    return result


def num_and_or(left, right_node: psr.Node, symbol, env: Environment):
    if left:
        if symbol == "||":
            return True
        elif symbol == "&&":
            right = evaluate(right_node, env)
            return right
        else:
            raise InterpretException("No such symbol")
    else:
        if symbol == "&&":
            return False
        elif symbol == "||":
            right = evaluate(right_node, env)
            return right
        else:
            raise InterpretException("No such symbol")


ARITHMETIC_TABLE = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
    "/": lambda left, right: left / right,
    "%": lambda left, right: left % right,
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    ">": lambda left, right: left > right,
    "<": lambda left, right: left < right,
    ">=": lambda left, right: left >= right,
    "<=": lambda left, right: left <= right,
    "<<": lambda left, right: left << right,
    ">>": lambda left, right: left >> right,
    "&": lambda left, right: left & right,
    "^": lambda left, right: left ^ right,
    "|": lambda left, right: left | right,
    "===": lambda left, right: left == right,
    "!==": lambda left, right: left != right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and right.name == type(left).__name__
}


def num_arithmetic(left, right, symbol):
    return ARITHMETIC_TABLE[symbol](left, right)


def class_inheritance(cla, env, scope):
    """

    :param cla:
    :type cla: Class
    :param env: the global environment
    :type env: Environment
    :param scope: the class scope
    :type scope: Environment
    :return:
    """
    for sc in cla.superclass_names:
        sc_ins = evaluate(sc, env)
        class_inheritance(sc_ins, env, scope)
        # class_inheritance(env.get_heap(sc), env, scope)

    evaluate(cla.body, scope)  # this step just fills the scope


def native_types_call(instance: NativeType, method: psr.FuncCall, env: Environment):
    """

    :param instance:
    :param method:
    :param env:
    :return:
    """
    args = []
    for x in method.args.lines:
        args.append(evaluate(x, env))
    name = method.f_name
    type_ = type(instance)
    method = getattr(type_, name)
    res = method(instance, *args)
    return res


def native_types_invoke(instance: NativeType, node: psr.NameNode):
    """

    :param instance:
    :param node:
    :return:
    """
    name = node.name
    type_ = type(instance)
    res = getattr(type_, name)
    return res


def self_return(node):
    return node


def eval_boolean_stmt(node: psr.BooleanStmt, env):
    if node.value == "true":
        return True
    elif node.value == "false":
        return False
    else:
        raise InterpretException("Unknown boolean value")


def eval_anonymous_call(node: psr.AnonymousCall, env: Environment):
    evaluate(node.left, env)
    right = node.right.args
    fc = psr.FuncCall((node.line_num, node.file), "=>")
    fc.args = right
    return evaluate(fc, env)


def eval_return(node: psr.ReturnStmt, env: Environment):
    value = node.value
    res = evaluate(value, env)
    # print(env.variables)
    env.terminate(res)
    return res


def eval_block(node: psr.BlockStmt, env: Environment):
    result = 0
    for line in node.lines:
        result = evaluate(line, env)
    return result


def eval_if_stmt(node: psr.IfStmt, env: Environment):
    cond = evaluate(node.condition, env)
    if cond:
        return evaluate(node.then_block, env)
    else:
        return evaluate(node.else_block, env)


def eval_while(node: psr.WhileStmt, env: Environment):
    result = 0
    while not env.broken and evaluate(node.condition, env):
        result = evaluate(node.body, env)
        env.paused = False  # reset the environment the the next iteration
    env.broken = False  # reset the environment for next loop
    return result


def eval_for_loop_stmt(node: psr.ForLoopStmt, env: Environment):
    arg_num = len(node.condition.lines)
    if arg_num == 3:
        return eval_for_loop(node, env)
    elif arg_num == 2:
        return eval_for_each_loop(node, env)
    else:
        raise InterpretException("Wrong argument number for 'for' loop, in {}, at line {}"
                                 .format(node.file, node.line_num))


def eval_def(node: psr.DefStmt, env: Environment):
    f = Function(node.params, node.presets, node.body)
    f.outer_scope = env

    if node.const:
        env.assign_const(node.name, f)
    else:
        env.assign(node.name, f)
    if node.auth == lex.PRIVATE:
        env.add_private(node.name)
    return f


def eval_class_stmt(node, env: Environment):
    cla = Class(node.class_name, node.block)
    cla.superclass_names = node.superclass_names
    env.add_heap(node.class_name, cla)
    return cla


def eval_import_stmt(node: psr.ImportStmt, env: Environment):
    scope = Environment(True, {})
    scope.scope_name = "Module " + node.class_name
    evaluate(node.block, scope)
    # print(scope)
    imp = Module(node.class_name, scope)
    env.add_heap(node.class_name, imp)
    # print(node.class_name)
    # print(env)
    # print(node.class_name)
    return imp


def eval_jump(node, env):
    func: Function = env.get(node.to, (0, "f"))
    for i in range(len(node.args.lines)):
        env.assign(func.params[i].name, evaluate(node.args.lines[i], env))
    return evaluate(func.body, env)


def raise_exception(e: Exception):
    raise e


# SELF_RETURN_TABLE = {"int", "float", "bool", "NoneType", "String", "List", "Set", "Pair", "System", "File"}
SELF_RETURN_TABLE_2 = {int, float, bool, String, List, Set, Pair, System, File}

NODE_TABLE = {
    psr.INT_NODE: lambda n, env: n.value,
    psr.FLOAT_NODE: lambda n, env: n.value,
    psr.LITERAL_NODE: lambda n, env: String(n.literal),
    psr.NAME_NODE: lambda n, env: env.get(n.name, (n.line_num, n.file)),
    psr.BOOLEAN_STMT: eval_boolean_stmt,
    psr.NULL_STMT: lambda n, env: None,
    psr.BREAK_STMT: lambda n, env: env.break_loop(),
    psr.CONTINUE_STMT: lambda n, env: env.pause_loop(),
    psr.ASSIGNMENT_NODE: assignment,
    psr.DOT: eval_dot,
    psr.ANONYMOUS_CALL: eval_anonymous_call,
    psr.OPERATOR_NODE: eval_operator,
    psr.NEGATIVE_EXPR: lambda n, env: -evaluate(n.value, env),
    psr.NOT_EXPR: lambda n, env: not bool(evaluate(n.value, env)),
    psr.RETURN_STMT: eval_return,
    psr.BLOCK_STMT: eval_block,
    psr.IF_STMT: eval_if_stmt,
    psr.WHILE_STMT: eval_while,
    psr.FOR_LOOP_STMT: eval_for_loop_stmt,
    psr.DEF_STMT: eval_def,
    psr.FUNCTION_CALL: call_function,
    psr.CLASS_STMT: eval_class_stmt,
    psr.CLASS_INIT: init_class,
    psr.INVALID_TOKEN: lambda n, env: raise_exception(InterpretException("Argument error, in {}, at line {}"
                                                                         .format(n.file, n.line_num))),
    psr.ABSTRACT: lambda n, env: raise_exception(
        AbstractMethodException("Method is not implemented, in {}, at line {}"
                                .format(n.file, n.line_num))),
    psr.THROW_STMT: lambda n, env: raise_exception(RuntimeException(evaluate(n.value, env))),
    psr.TRY_STMT: eval_try_catch,
    psr.JUMP_NODE: eval_jump,
    psr.IMPORT_STMT: eval_import_stmt,
    psr.NAMESPACE: eval_namespace
}


def evaluate(node: psr.Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding working environment.

    :param node: the node in abstract syntax tree to be evaluated
    :param env: the working environment
    :return: the evaluation result
    """
    if env.terminated:
        return env.exit_value
    if env.paused or node is None:
        return None
    if type(node) in SELF_RETURN_TABLE_2:
        return node
    t = node.node_type
    node.execution += 1
    tn = NODE_TABLE[t]
    return tn(node, env)
    # else:
    #     raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))
