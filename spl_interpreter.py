import spl_ast as ast
import spl_lexer as lex
import spl_parser as psr
import time as time_lib
import spl_token_lib as stl
import sys

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]

GLOBAL_SCOPE = 0
CLASS_SCOPE = 1
FUNCTION_SCOPE = 2
LOOP_SCOPE = 3
SUB_SCOPE = 4

# LOCAL_SCOPES = {LOOP_SCOPE, IF_ELSE_SCOPE, TRY_CATCH_SCOPE, LOOP_INNER_SCOPE}

LINE_FILE = 0, "interpreter"
INVALID = ast.InvalidToken(LINE_FILE)


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    :type encoding: str
    """

    def __init__(self, argv, encoding):
        self.ast = None
        self.argv = argv
        self.env = Environment(GLOBAL_SCOPE, None)
        self.env.add_heap("system", System(List(*parse_args(argv)), encoding))
        self.env.scope_name = "Global"

    def set_ast(self, ast_: ast.BlockStmt):
        """
        Sets up the abstract syntax tree to be interpreted.

        :param ast_: the root of the abstract syntax tree to be interpreted
        :return: None
        """
        self.ast = ast_

    def interpret(self):
        """
        Starts the interpretation.

        :return: the exit value
        """
        return evaluate(self.ast, self.env)


def parse_args(argv):
    """

    :param argv: the system argv
    :return: the argv in spl String object
    """
    return [String(x) for x in argv]


class Counter:
    def __init__(self):
        self.count = 0

    def decrement(self):
        self.count -= 1

    def get_and_increment(self):
        temp = self.count
        self.count += 1
        return temp


ID_COUNTER = Counter()


class Environment:
    heap: dict
    variables: dict
    scope_type: int

    """
    ===== Attributes =====
    :param scope_type: the type of scope, whether it is global, class, function or inner
    """

    def __init__(self, scope_type, outer):
        self.scope_type = scope_type
        if outer is not None:
            self.heap: dict = outer.heap  # Heap-allocated variables (global)
        else:
            self.heap: dict = {}
        self.variables: dict = {}  # Stack variables
        self.constants: dict = {}  # Constants
        # self.locals: dict = {}  # Local variables
        # self.privates = set()

        self.outer: Environment = outer
        self.scope_name = None

        # environment signals
        self.terminated = False
        self.exit_value = None
        self.broken = False
        self.paused = False

        if not self.is_sub():
            self.variables.__setitem__("=>", None)

        if self.is_global():
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
        return "".join(['null' if k is None else k for k in temp])

    def invalidate(self):
        self.variables.clear()
        self.constants.clear()

    def is_global(self):
        return self.scope_type == GLOBAL_SCOPE

    def is_sub(self):
        return self.scope_type == LOOP_SCOPE or self.scope_type == SUB_SCOPE

    def _add_natives(self):
        self.add_heap("print", NativeFunction(print_, "print"))
        self.add_heap("println", NativeFunction(print_ln, "println"))
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
        self.add_heap("getcwf", NativeFunction(getcwf, "getcwf", self))
        self.add_heap("main", NativeFunction(is_main, "main", self))
        self.add_heap("exit", NativeFunction(exit_, "exit"))
        self.add_heap("help", NativeFunction(help_, "help", self))

        # type of built-in
        self.add_heap("boolean", NativeFunction(to_boolean, "boolean"))
        self.add_heap("void", NativeFunction(None, "void"))

        self.add_heap("cwf", None)

    def add_heap(self, k, v):
        self.heap[k] = v

    def terminate(self, exit_value):
        if self.scope_type == FUNCTION_SCOPE:
            self.terminated = True
            self.exit_value = exit_value
        elif self.is_sub():
            if self.scope_type == LOOP_SCOPE:
                self.broken = True
            self.outer.terminate(exit_value)
        else:
            raise SplException("Return outside function.")

    def is_terminated(self):
        if self.scope_type == FUNCTION_SCOPE:
            return self.terminated
        elif self.is_sub():
            return self.outer.is_terminated()
        else:
            return False

    def terminate_value(self):
        if self.scope_type == FUNCTION_SCOPE:
            return self.exit_value
        elif self.is_sub():
            return self.outer.terminate_value()
        else:
            raise SplException("Terminate value outside function.")

    def break_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.broken = True
        elif self.is_sub():
            self.outer.break_loop()
        else:
            raise SplException("Break not inside loop.")

    def pause_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.paused = True
        elif self.is_sub():
            self.outer.pause_loop()
        else:
            raise SplException("Continue not inside loop.")

    def resume_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.paused = False
        elif self.is_sub():
            self.outer.resume_loop()
        else:
            raise SplException("Not inside loop.")

    def define_function(self, key, value, lf, override: bool):
        if not override and key[0].islower() and self.contains_key(key):
            stl.print_waring("Warning: re-declaring function '{}' in '{}', at line {}".format(key, lf[1], lf[0]))
        self.variables[key] = value

    def define_var(self, key, value, lf):
        if self.contains_key(key):
            raise SplException("Name '{}' is already defined in this scope, in '{}', at line {}"
                               .format(key, lf[1], lf[0]))
        else:
            self.variables[key] = value

    def define_const(self, key, value, lf):
        # if key in self.constants:
        if self.contains_key(key):
            raise SplException("Name '{}' is already defined in this scope, in {}, at line {}"
                               .format(key, lf[1], lf[0]))
        else:
            self.constants[key] = value

    def assign(self, key, value, lf):
        if key in self.constants:
            raise SplException("Re-assignment to constant values, in '{}', at line {}"
                               .format(key, lf[1], lf[0]))
        elif key in self.variables:
            self.variables[key] = value
        else:
            out = self.outer
            while out:
                if key in out.constants:
                    raise SplException("Re-assignment to constant values, in '{}', at line {}"
                                       .format(key, lf[1], lf[0]))
                if key in out.variables:
                    out.variables[key] = value
                    return
                out = out.outer
            raise SplException("Name '{}' is not defined, in '{}', at line {}"
                               .format(key, lf[1], lf[0]))

    def inner_get(self, key: str):
        if key in self.constants:
            return self.constants[key]
        elif key in self.variables:
            return self.variables[key]

        out = self.outer
        while out:
            if key in out.constants:
                return out.constants[key]
            elif key in out.variables:
                return out.variables[key]

            out = out.outer

        if key in self.heap:
            return self.heap[key]
        else:
            return NULLPTR

    def get(self, key: str, line_file: tuple):
        """
        Returns the value of that key.

        :param key:
        :param line_file:
        :return:
        """
        v = self.inner_get(key)
        # print(key + str(v))
        if v is NULLPTR:
            raise SplException("Name '{}' is not defined, in file {}, at line {}"
                               .format(key, line_file[1], line_file[0]))
        else:
            return v

    def contains_key(self, key: str):
        v = self.inner_get(key)
        if v is NULLPTR:
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


class ParameterPair:
    def __init__(self, name: str, preset):
        self.name: str = name
        self.preset = preset

    def __str__(self):
        return "{}={}".format(self.name, self.preset)

    def __repr__(self):
        return self.__str__()


class Function:
    """
    :type body: BlockStmt
    :type outer_scope: Environment
    """

    def __init__(self, params, body, outer, abstract: bool):
        # self.name = f_name
        self.params: [ParameterPair] = params
        # self.presets: list = presets
        self.body = body
        self.outer_scope = outer
        self.abstract = abstract
        self.file = None
        self.line_num = None

    def __str__(self):
        return "Function<{}>".format(id(self))

    def __repr__(self):
        return self.__str__()


class Class:
    def __init__(self, class_name: str, body: ast.BlockStmt, abstract: bool):
        self.class_name = class_name
        self.body = body
        self.superclass_names = []
        self.outer_env = None
        self.abstract = abstract
        self.line_num = None
        self.file = None

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

    # def __eq__(self, other):
    #     return isinstance(other, NullPointer)

    def __str__(self):
        return "NullPointer"


class Undefined:
    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, Undefined)

    def __str__(self):
        return "undefined"

    def __repr__(self):
        return self.__str__()


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
    argv: List
    encoding: str

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


# Native functions

def print_ln(*args):
    if len(args) > 0:
        a0 = args[0]
        s = stl.replace_bool_none(str(a0))
        # print(s, *args[1:])
        sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return None


def print_(*args):
    a0 = args[0]
    s = stl.replace_bool_none(str(a0))
    sys.stdout.write(s)
    return None


def input_(*prompt):
    s = input(*prompt)
    return String(s)


def typeof(obj) -> String:
    if obj is None:
        return String("void")
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
    lexer = lex.Tokenizer()
    lexer.file_name = "expression"
    lexer.script_dir = "expression"
    lexer.tokenize([expr.text()])
    parser = psr.Parser(lexer.get_tokens())
    block = parser.parse()
    return block


def dir_(env, obj):
    """
    Returns a List containing all attributes of a type or an object.

    :param env:
    :param obj:
    :return:
    """
    lst = List()
    if isinstance(obj, Class):
        # instance = inter.ClassInstance(env, obj.class_name)
        create = ast.ClassInit((0, "dir"), obj.class_name)
        instance: ClassInstance = evaluate(create, env)
        exc = {"=>", "this"}
        # for attr in instance.env.variables:
        for attr in instance.env.attributes():
            if attr not in exc:
                lst.append(attr)
        del instance
        ID_COUNTER.decrement()
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


def getcwf(env: Environment):
    return env.get_heap("cwf")


def is_main(env: Environment):
    return env.get_heap("system").argv[0] == getcwf(env)


def exit_(code=0):
    exit(code)


def help_(env, obj):
    if isinstance(obj, NativeFunction):
        pass
    elif isinstance(obj, Function):
        print(obj)
    elif isinstance(obj, Class):
        cla_self = _get_doc(obj)
        print("Help on class", obj.class_name, "\n")
        title = ["class ", obj.class_name]
        if len(obj.superclass_names) > 0:
            title.append(" extends ")
            for x in obj.superclass_names:
                title.append(x)
                title.append(", ")
            title.pop()
        print("".join(title))
        print(cla_self)
        print("---------- Attributes ----------")

        create = ast.ClassInit((0, "dir"), obj.class_name)
        instance: ClassInstance = evaluate(create, env)
        ID_COUNTER.decrement()
        exc = {"this"}
        # for attr in instance.env.variables:
        for attr in instance.env.attributes():
            if attr not in exc:
                print(attr)
                print(_get_doc(instance.env.get(attr, (0, "help"))))


# Helper functions

def _get_doc(obj):
    if isinstance(obj, Class) or isinstance(obj, Function) or isinstance(obj, ast.Node):
        doc_file = stl.get_doc_name(obj.file)
        try:
            with open(doc_file, "r") as f:
                lines = f.readlines()

            pos = obj.line_num - 1
            result = []
            result.extend(_filter_doc(lines, pos))
            return "".join(result)
        except IOError:
            return "| "
    else:
        return "| " + typeof(obj).literal


def _filter_doc(lines: [str], pos: int):
    """

    :param lines:
    :return:
    """
    lst = []
    in_doc = False
    for i in range(pos - 1, -1, -1):
        line = lines[i]
        if not in_doc:
            if line[0] == "+":
                break
            elif line[0] == "*":
                lst.append("| ")
                lst.append(line[1:])
    return lst


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


# Interpreter

NULLPTR = NullPointer()
UNDEFINED = Undefined()

PRIMITIVE_FUNC_TABLE = {
    "boolean": "bool",
    "void": "NoneType"
}


class ClassInstance:
    def __init__(self, env: Environment, class_name: str):
        """
        ===== Attributes =====
        :param class_name: name of this class
        :param env: instance attributes
        """
        self.class_name = class_name
        self.env = env
        self.id = ID_COUNTER.get_and_increment()
        # self.reference_count = 0
        self.env.constants["this"] = self

    def __hash__(self):
        if self.env.contains_key("__hash__"):
            call = ast.FuncCall(LINE_FILE, "__hash__")
            call.args = []
            return evaluate(call, self.env)
        else:
            return hash(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.env.contains_key("__str__"):
            call = ast.FuncCall(LINE_FILE, "__str__")
            call.args = []
            return str(evaluate(call, self.env))
        else:
            attr = self.env.attributes()
            attr.pop("this")
            attr.pop("=>")
            return "<{} at {}>: {}".format(self.class_name, self.id, attr)


class RuntimeException(Exception):
    def __init__(self, exception: ClassInstance):
        Exception.__init__(self, "RuntimeException")

        self.exception = exception


def eval_for_loop(node: ast.ForLoopStmt, env: Environment):
    con: ast.BlockStmt = node.condition
    start = con.lines[0]
    end = con.lines[1]
    step = con.lines[2]

    title_scope = Environment(LOOP_SCOPE, env)
    title_scope.scope_name = "Loop title"

    block_scope = Environment(SUB_SCOPE, title_scope)
    block_scope.scope_name = "Block scope for"

    result = evaluate(start, title_scope)

    while not title_scope.broken and evaluate(end, title_scope):
        block_scope.invalidate()
        result = evaluate(node.body, block_scope)
        title_scope.resume_loop()
        evaluate(step, title_scope)

    del title_scope
    del block_scope
    return result


def eval_for_each_loop(node: ast.ForLoopStmt, env: Environment):
    con: ast.BlockStmt = node.condition
    inv: ast.Node = con.lines[0]
    lf = node.line_num, node.file

    title_scope = Environment(LOOP_SCOPE, env)
    title_scope.scope_name = "Loop title"

    block_scope = Environment(SUB_SCOPE, title_scope)
    block_scope.scope_name = "Block scope for each"

    if inv.node_type == ast.NAME_NODE:
        inv: ast.NameNode
        invariant = inv.name
    elif inv.node_type == ast.ASSIGNMENT_NODE:
        inv: ast.AssignmentNode
        evaluate(inv, title_scope)
        invariant = inv.left.name
    else:
        raise SplException("Unknown type for for-each loop invariant")
    target = con.lines[1]
    # print(target)
    iterable = evaluate(target, title_scope)
    if isinstance(iterable, Iterable):
        result = None
        for x in iterable:
            block_scope.invalidate()
            block_scope.assign(invariant, x, lf)
            result = evaluate(node.body, block_scope)
            title_scope.resume_loop()
            if title_scope.broken:
                break

        del title_scope
        del block_scope
        # env.broken = False
        return result
    elif isinstance(iterable, ClassInstance) and is_subclass_of(title_scope.get_heap(iterable.class_name), "Iterable",
                                                                title_scope):
        ite = ast.FuncCall(lf, "__iter__")
        iterator: ClassInstance = evaluate(ite, iterable.env)
        result = None
        while not title_scope.broken:
            block_scope.invalidate()
            nex = ast.FuncCall(lf, "__next__")
            res = evaluate(nex, iterator.env)
            if isinstance(res, ClassInstance) and is_subclass_of(title_scope.get_heap(res.class_name), "StopIteration",
                                                                 title_scope):
                break
            block_scope.assign(invariant, res, lf)
            result = evaluate(node.body, block_scope)
            title_scope.resume_loop()
        # env.broken = False
        del title_scope
        del block_scope
        return result
    else:
        raise SplException(
            "For-each loop on non-iterable objects, in {}, at line {}".format(node.file, node.line_num))


def eval_try_catch(node: ast.TryStmt, env: Environment):
    try:
        block_scope = Environment(SUB_SCOPE, env)
        block_scope.scope_name = "Try scope"
        result = evaluate(node.try_block, block_scope)
        # env.terminated = False
        return result
    except RuntimeException as re:  # catches the exceptions thrown by SPL program
        block_scope = Environment(SUB_SCOPE, env)
        block_scope.scope_name = "Catch scope"
        exception: ClassInstance = re.exception
        exception_class = block_scope.get_heap(exception.class_name)
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                if is_subclass_of(exception_class, catch_name, block_scope):
                    result = evaluate(cat.then, block_scope)
                    # env.terminated = False
                    return result
                    # if node.finally_block is None:
                    #     return result
                    # else:
                    #     env.terminated = False
        raise re
    except Exception as e:  # catches the exceptions raised by python
        block_scope = Environment(SUB_SCOPE, env)
        block_scope.scope_name = "Try scope"
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                # exception_name = exception.class_name
                if catch_name == "Exception":
                    result = evaluate(cat.then, block_scope)
                    # env.terminated = False
                    return result
        raise e
    finally:
        block_scope = Environment(SUB_SCOPE, env)
        block_scope.scope_name = "Finally scope"
        if node.finally_block is not None:
            return evaluate(node.finally_block, block_scope)


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


def eval_operator(node: ast.OperatorNode, env: Environment):
    left = evaluate(node.left, env)
    if node.assignment:
        right = evaluate(node.right, env)
        symbol = node.operation[:-1]
        res = arithmetic(left, right, symbol, env)
        asg = ast.AssignmentNode((node.line_num, node.file), False)
        asg.left = node.left
        asg.operation = "="
        asg.right = res
        return evaluate(asg, env)
    else:
        symbol = node.operation
        right_node = node.right
        return arithmetic(left, right_node, symbol, env)


def assignment(node: ast.AssignmentNode, env: Environment):
    key = node.left
    value = evaluate(node.right, env)
    t = key.node_type
    lf = node.line_num, node.file
    # print(key)
    if t == ast.NAME_NODE:
        key: ast.NameNode
        if node.level == ast.ASSIGN:
            env.assign(key.name, value, lf)
        elif node.level == ast.CONST:
            env.define_const(key.name, value, lf)
        elif node.level == ast.VAR:
            env.define_var(key.name, value, lf)
        else:
            raise SplException("Unknown variable level")
        return value
    elif t == ast.DOT:
        if node.level == ast.CONST:
            raise SplException("Unsolved syntax: assigning a constant to an instance")
        node = key
        name_lst = []
        while isinstance(node, ast.Dot):
            name_lst.append(node.right.name)
            node = node.left
        name_lst.append(node.name)
        name_lst.reverse()
        # print(name_lst)
        scope = env
        for t in name_lst[:-1]:
            scope = scope.get(t, (node.line_num, node.file)).env
        scope.assign(name_lst[-1], value, lf)
        return value
    else:
        raise InterpretException("Unknown assignment, in {}, at line {}".format(node.file, node.line_num))


def init_class(node: ast.ClassInit, env: Environment):
    cla: Class = env.get_heap(node.class_name)

    if cla.abstract:
        raise SplException("Abstract class is not instantiable")

    scope = Environment(CLASS_SCOPE, cla.outer_env)
    # scope.outer = env
    scope.scope_name = "Class scope<{}>".format(cla.class_name)
    class_inheritance(cla, env, scope)

    # print(scope.variables)
    instance = ClassInstance(scope, node.class_name)
    attrs = scope.attributes()
    for k in attrs:
        v = attrs[k]
        if isinstance(v, Function):
            v.outer_scope = scope

    if node.args:
        # constructor: Function = scope.variables[node.class_name]
        fc = ast.FuncCall((node.line_num, node.file), node.class_name)
        fc.args = node.args
        func = scope.get(node.class_name, (node.line_num, node.file))
        call_function(fc, func, scope, env)
    return instance


def eval_func_call(node: ast.FuncCall, env: Environment):
    lf = node.line_num, node.file
    func = env.get(node.f_name, lf)

    if isinstance(func, Function):
        result = call_function(node, func, func.outer_scope, env)
        return result
    elif isinstance(func, NativeFunction):
        args = []
        for i in range(len(node.args.lines)):
            # args.append(evaluate(node.args[i], env))
            args.append(evaluate(node.args.lines[i], env))
        result = func.call(args)
        if isinstance(result, ast.BlockStmt):
            # Special case for "eval"
            res = evaluate(result, env)
            return res
        else:
            return result
    else:
        raise InterpretException("Not a function call, in {}, at line {}.".format(node.file, node.line_num))


def call_function(call: ast.FuncCall, func: Function, func_parent_env: Environment, call_env: Environment) \
        -> object:
    """
    Calls a function

    :param call: the call
    :param func: the function object itself
    :param func_parent_env: the parent environment of the function where it was defined
    :param call_env: the environment where the function call was made
    :return: the function result
    """
    lf = call.line_num, call.file

    if func.abstract:
        raise AbstractMethodException("Abstract method is not callable, in '{}', at line {}."
                                      .format(call.file, call.line_num))

    scope = Environment(FUNCTION_SCOPE, func.outer_scope)
    scope.scope_name = "Function scope<{}>".format(call.f_name)

    params = func.params

    args = call.args.lines

    pos_args = []  # Positional arguments
    kwargs = {}  # Keyword arguments

    for arg in args:
        if isinstance(arg, ast.AssignmentNode):
            kwargs[arg.left.name] = arg.right
        else:
            pos_args.append(arg)
    # print(pos_args)
    # print(kwargs)
    if len(pos_args) + len(kwargs) > len(params):
        raise ArgumentException("Too many arguments for function '{}', in file '{}', at line {}"
                                .format(call.f_name, call.file, call.line_num))
    for i in range(len(params)):
        # Assign function arguments
        param: ParameterPair = params[i]
        if i < len(pos_args):
            arg = pos_args[i]
        elif param.name in kwargs:
            arg = kwargs[param.name]
        elif param.preset is not INVALID:
            arg = param.preset
        else:
            raise ArgumentException("Function '{}' missing a positional argument '{}', in file '{}', at line {}"
                                    .format(call.f_name, param.name, call.file, call.line_num))

        e = evaluate(arg, call_env)
        scope.define_var(param.name, e, lf)
    result = evaluate(func.body, scope)
    func_parent_env.assign("=>", result, lf)
    return result


def eval_dot(node: ast.Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.node_type
    # print(node.left)
    if t == ast.NAME_NODE:
        obj: ast.NameNode
        if obj.name == "this":
            raise UnauthorizedException("Access 'this' from outside")
        if isinstance(instance, NativeType):
            return native_types_invoke(instance, obj)
        elif isinstance(instance, ClassInstance):
            attr = instance.env.get(obj.name, (node.line_num, node.file))
            return attr
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    elif t == ast.FUNCTION_CALL:
        obj: ast.FuncCall
        if isinstance(instance, NativeType):
            try:
                return native_types_call(instance, obj, env)
            except IndexError as ie:
                raise IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                               .format(node.file, node.line_num))
        elif isinstance(instance, ClassInstance):
            # instance.env.use_temp_var = True
            # for arg in obj.args.lines:
            #     instance.env.temp_vars.append(evaluate(arg, env))
            lf = node.line_num, node.file
            func: Function = instance.env.get(obj.f_name, lf)
            result = call_function(obj, func, instance.env, env)

            env.assign("=>", result, lf)
            return result
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    else:
        raise InterpretException("Unknown Syntax")


def arithmetic(left, right_node: ast.Node, symbol, env: Environment):
    if symbol in stl.LAZY:
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
        return isinstance(right, ClassInstance) and left.id == right.id
    elif symbol == "!==":
        return not isinstance(right, ClassInstance) or left.id != right.id
    elif symbol == "instanceof":
        if isinstance(right, Class):
            return is_subclass_of(env.get_heap(left.class_name), right.class_name, env)
        elif isinstance(right_node, ast.NameNode) and isinstance(right, Function):
            right_extra = env.get_heap(right_node.name)
            return is_subclass_of(env.get_heap(left.class_name), right_extra.class_name, env)
        else:
            return False
    else:
        fc = ast.FuncCall(LINE_FILE, "__" + stl.BINARY_OPERATORS[symbol] + "__")
        block = ast.BlockStmt(LINE_FILE)
        block.add_line(right)
        fc.args = block
        func: Function = left.env.get(fc.f_name, LINE_FILE)
        result = call_function(fc, func, left.env, env)
        return result


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
        raise TypeException("Unsupported operation between string and " + typeof(right).literal)

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


def primitive_and_or(left, right_node: ast.Node, symbol, env: Environment):
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


def num_and_or(left, right_node: ast.Node, symbol, env: Environment):
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


def class_inheritance(cla: Class, env: Environment, scope: Environment):
    """

    :param cla:
    :param env: the global environment
    :param scope: the class scope
    :return: None
    """
    # print(cla)
    for sc in cla.superclass_names:
        class_inheritance(env.get_heap(sc), env, scope)

    evaluate(cla.body, scope)  # this step just fills the scope


def native_types_call(instance: NativeType, method: ast.FuncCall, env: Environment):
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


def native_types_invoke(instance: NativeType, node: ast.NameNode):
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


def eval_boolean_stmt(node: ast.BooleanStmt, env):
    if node.value == "true":
        return True
    elif node.value == "false":
        return False
    else:
        raise InterpretException("Unknown boolean value")


def eval_anonymous_call(node: ast.AnonymousCall, env: Environment):
    evaluate(node.left, env)
    right = node.right.args
    fc = ast.FuncCall((node.line_num, node.file), "=>")
    fc.args = right
    return evaluate(fc, env)


def eval_return(node: ast.ReturnStmt, env: Environment):
    value = node.value
    res = evaluate(value, env)
    # print(env.variables)
    env.terminate(res)
    return res


def eval_block(node: ast.BlockStmt, env: Environment):
    result = None
    for line in node.lines:
        result = evaluate(line, env)
    return result


def eval_if_stmt(node: ast.IfStmt, env: Environment):
    cond = evaluate(node.condition, env)
    block_scope = Environment(SUB_SCOPE, env)
    block_scope.scope_name = "Block scope if-else"
    if cond:
        return evaluate(node.then_block, block_scope)
    else:
        return evaluate(node.else_block, block_scope)


def eval_while(node: ast.WhileStmt, env: Environment):
    title_scope = Environment(LOOP_SCOPE, env)
    title_scope.scope_name = "While loop title"

    block_scope = Environment(SUB_SCOPE, title_scope)
    block_scope.scope_name = "Block scope while loop"

    result = 0
    while not title_scope.broken and evaluate(node.condition, title_scope):
        block_scope.invalidate()
        result = evaluate(node.body, block_scope)
        title_scope.resume_loop()

    del title_scope
    del block_scope
    return result


def eval_for_loop_stmt(node: ast.ForLoopStmt, env: Environment):
    arg_num = len(node.condition.lines)
    if arg_num == 3:
        return eval_for_loop(node, env)
    elif arg_num == 2:
        return eval_for_each_loop(node, env)
    else:
        raise InterpretException("Wrong argument number for 'for' loop, in {}, at line {}"
                                 .format(node.file, node.line_num))


def eval_def(node: ast.DefStmt, env: Environment):
    block: ast.BlockStmt = node.params
    params_lst = []
    # print(block)
    for p in block.lines:
        # p: ast.Node
        if p.node_type == ast.NAME_NODE:
            p: ast.NameNode
            name = p.name
            value = INVALID
        elif p.node_type == ast.ASSIGNMENT_NODE:
            p: ast.AssignmentNode
            name = p.left.name
            value = evaluate(p.right, env)
        else:
            raise SplException("Unexpected syntax in function parameter, in file '{}', at line {}."
                               .format(node.file, node.line_num))
        pair = ParameterPair(name, value)
        params_lst.append(pair)

    f = Function(params_lst, node.body, env, node.abstract)
    f.file = node.file
    f.line_num = node.line_num
    override = "Override" in node.titles
    env.define_function(node.name, f, (node.line_num, node.file), override)

    return f


def eval_class_stmt(node: ast.ClassStmt, env: Environment):
    cla = Class(node.class_name, node.block, node.abstract)
    cla.superclass_names = node.superclass_names
    cla.outer_env = env
    cla.line_num, cla.file = node.line_num, node.file
    env.add_heap(node.class_name, cla)
    return cla


def eval_jump(node, env: Environment):
    func: Function = env.get(node.to, (0, "f"))
    lf = node.line_num, node.file
    for i in range(len(node.args.lines)):
        env.assign(func.params[i].name, evaluate(node.args.lines[i], env), lf)
    return evaluate(func.body, env)


def raise_exception(e: Exception):
    raise e


SELF_RETURN_TABLE = {int, float, bool, String, List, Set, Pair, System, File, ClassInstance}

NODE_TABLE = {
    ast.INT_NODE: lambda n, env: n.value,
    ast.FLOAT_NODE: lambda n, env: n.value,
    ast.LITERAL_NODE: lambda n, env: String(n.literal),
    ast.NAME_NODE: lambda n, env: env.get(n.name, (n.line_num, n.file)),
    ast.BOOLEAN_STMT: eval_boolean_stmt,
    ast.NULL_STMT: lambda n, env: None,
    ast.BREAK_STMT: lambda n, env: env.break_loop(),
    ast.CONTINUE_STMT: lambda n, env: env.pause_loop(),
    ast.ASSIGNMENT_NODE: assignment,
    ast.DOT: eval_dot,
    ast.ANONYMOUS_CALL: eval_anonymous_call,
    ast.OPERATOR_NODE: eval_operator,
    ast.NEGATIVE_EXPR: lambda n, env: -evaluate(n.value, env),
    ast.NOT_EXPR: lambda n, env: not bool(evaluate(n.value, env)),
    ast.RETURN_STMT: eval_return,
    ast.BLOCK_STMT: eval_block,
    ast.IF_STMT: eval_if_stmt,
    ast.WHILE_STMT: eval_while,
    ast.FOR_LOOP_STMT: eval_for_loop_stmt,
    ast.DEF_STMT: eval_def,
    ast.FUNCTION_CALL: eval_func_call,
    ast.CLASS_STMT: eval_class_stmt,
    ast.CLASS_INIT: init_class,
    ast.INVALID_TOKEN: lambda n, env: raise_exception(InterpretException("Argument error, in {}, at line {}"
                                                                         .format(n.file, n.line_num))),
    ast.THROW_STMT: lambda n, env: raise_exception(RuntimeException(evaluate(n.value, env))),
    ast.TRY_STMT: eval_try_catch,
    ast.JUMP_NODE: eval_jump,
    ast.UNDEFINED_NODE: lambda n, env: UNDEFINED
}


def evaluate(node: ast.Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding working environment.

    :param node: the node in abstract syntax tree to be evaluated
    :param env: the working environment
    :return: the evaluation result
    """
    if env.is_terminated():
        return env.terminate_value()
    if node is None:
        return None
    if type(node) in SELF_RETURN_TABLE:
        return node
    t = node.node_type
    node.execution += 1
    tn = NODE_TABLE[t]
    env.add_heap("cwf", String(node.file))
    return tn(node, env)
