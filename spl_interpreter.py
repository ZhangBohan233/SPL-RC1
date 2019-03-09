import spl_ast as ast
import spl_lexer as lex
import spl_parser as psr
import spl_token_lib as stl
import spl_lib as lib
import multiprocessing

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]

GLOBAL_SCOPE = 0
CLASS_SCOPE = 1
FUNCTION_SCOPE = 2
LOOP_SCOPE = 3
SUB_SCOPE = 4

# LOCAL_SCOPES = {LOOP_SCOPE, IF_ELSE_SCOPE, TRY_CATCH_SCOPE, LOOP_INNER_SCOPE}

LINE_FILE = 0, "interpreter"
INVALID = lib.InvalidArgument()
UNPACK_ARGUMENT = lib.UnpackArgument()
KW_UNPACK_ARGUMENT = lib.KwUnpackArgument()


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    :type encoding: str
    """

    def __init__(self, argv, encoding):
        self.ast = None
        self.argv = argv
        self.encoding = encoding
        self.env = Environment(GLOBAL_SCOPE, None)
        self.env.scope_name = "Global"
        self.set_up_env()

    def set_up_env(self):
        add_natives(self.env)
        self.env.add_heap("system", lib.System(lib.List(*parse_args(self.argv)), self.encoding))
        self.env.add_heap("natives", NativeInvokes())

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
    return [lib.String(x) for x in argv]


def add_natives(self):
    self.add_heap("print", NativeFunction(lib.print_, "print"))
    self.add_heap("println", NativeFunction(lib.print_ln, "println"))
    self.add_heap("type", NativeFunction(typeof, "type"))
    self.add_heap("pair", NativeFunction(lib.make_pair, "pair"))
    self.add_heap("list", NativeFunction(lib.make_list, "list"))
    self.add_heap("set", NativeFunction(lib.make_set, "set"))
    self.add_heap("int", NativeFunction(lib.to_int, "int"))
    self.add_heap("float", NativeFunction(lib.to_float, "float"))
    self.add_heap("string", NativeFunction(to_str, "string"))
    self.add_heap("input", NativeFunction(lib.input_, "input"))
    self.add_heap("f_open", NativeFunction(lib.f_open, "f_open"))
    self.add_heap("eval", NativeFunction(eval_, "eval"))
    self.add_heap("dir", NativeFunction(dir_, "dir", self))
    self.add_heap("getcwf", NativeFunction(getcwf, "getcwf", self))
    self.add_heap("main", NativeFunction(is_main, "main", self))
    self.add_heap("exit", NativeFunction(lib.exit_, "exit"))
    self.add_heap("help", NativeFunction(help_, "help", self))

    # type of built-in
    self.add_heap("boolean", NativeFunction(lib.to_boolean, "boolean"))
    self.add_heap("void", NativeFunction(None, "void"))

    self.add_heap("cwf", None)


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
        if outer is None:
            self.heap: dict = {}
        else:
            self.heap: dict = outer.heap  # Heap-allocated variables (global)
        self.variables: dict = {}  # Stack variables
        self.constants: dict = {}  # Constants

        self.outer: Environment = outer
        self.scope_name = None

        # environment signals
        self.terminated = False
        self.exit_value = None
        self.broken = False
        self.paused = False

        if not self.is_sub():
            self.variables.__setitem__("=>", None)

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
            raise lib.SplException("Return outside function.")

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
            raise lib.SplException("Terminate value outside function.")

    def break_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.broken = True
        elif self.is_sub():
            self.outer.break_loop()
        else:
            raise lib.SplException("Break not inside loop.")

    def pause_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.paused = True
        elif self.is_sub():
            self.outer.pause_loop()
        else:
            raise lib.SplException("Continue not inside loop.")

    def resume_loop(self):
        if self.scope_type == LOOP_SCOPE:
            self.paused = False
        elif self.is_sub():
            self.outer.resume_loop()
        else:
            raise lib.SplException("Not inside loop.")

    def define_function(self, key, value, lf, options: dict):
        if not options["override"] and not options["suppress"] and key[0].islower() and self.contains_key(key):
            lib.print_waring("Warning: re-declaring method '{}' in '{}', at line {}".format(key, lf[1], lf[0]))
        self.variables[key] = value

    def define_var(self, key, value, lf):
        if self.contains_key(key):
            raise lib.SplException("Name '{}' is already defined in this scope, in '{}', at line {}"
                                   .format(key, lf[1], lf[0]))
        else:
            self.variables[key] = value

    def define_const(self, key, value, lf):
        # if key in self.constants:
        if self.contains_key(key):
            raise lib.SplException("Name '{}' is already defined in this scope, in {}, at line {}"
                                   .format(key, lf[1], lf[0]))
        else:
            self.constants[key] = value

    def assign(self, key, value, lf):
        if key in self.variables:
            self.variables[key] = value
        else:
            out = self.outer
            while out:
                if key in out.variables:
                    out.variables[key] = value
                    return
                out = out.outer
            raise lib.SplException("Name '{}' is not defined, in '{}', at line {}"
                                   .format(key, lf[1], lf[0]))

    def inner_get(self, key: str):
        """
        Internally gets a value stored in this scope, 'NULLPTR' if not found.

        :param key:
        :return:
        """
        if key in self.constants:
            return self.constants[key]
        if key in self.variables:
            return self.variables[key]

        out = self.outer
        while out:
            if key in out.constants:
                return out.constants[key]
            if key in out.variables:
                return out.variables[key]

            out = out.outer

        return self.heap.get(key, NULLPTR)

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
            raise lib.SplException("Name '{}' is not defined, in file {}, at line {}"
                                   .format(key, line_file[1], line_file[0]))
        else:
            return v

    def contains_key(self, key: str):
        v = self.inner_get(key)
        return v is not NULLPTR

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

    def call(self, args, kwargs):
        if self.parent_env:
            if len(kwargs) > 0:
                return self.function(self.parent_env, *args, kwargs)
            else:
                return self.function(self.parent_env, *args)
        else:
            if len(kwargs) > 0:
                return self.function(*args, kwargs)
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


class Thread(lib.NativeType):
    def __init__(self, process):
        lib.NativeType.__init__(self)

        self.process: multiprocessing.Process = process
        self.daemon = False

    def type_name(self):
        return "thread"

    def set_daemon(self, d):
        self.daemon = d

    def start(self):
        self.process.daemon = self.daemon
        self.process.start()

    def alive(self):
        return self.process.is_alive()


class NativeInvokes(lib.NativeType):
    def __init__(self):
        lib.NativeType.__init__(self)

    def type_name(self):
        return "natives"

    def str_join(self, s: lib.String, itr):
        if isinstance(itr, lib.Iterable):
            return lib.String(s.literal.join([x.text() for x in itr]))
        else:
            raise lib.TypeException("Object is not a native-iterable object.")

    def thread(self, env: Environment, target: Function, name: str, args: lib.List):
        call = ast.FuncCall(LINE_FILE, name)
        call.args = ast.BlockStmt(LINE_FILE)
        for x in args.list:
            call.args.lines.append(x)

        process = multiprocessing.Process(target=call_function, args=(call, target, target.outer_scope, env))
        return Thread(process)


# Native functions with dependencies

def to_str(v) -> lib.String:
    if isinstance(v, ClassInstance):
        fc: ast.FuncCall = ast.FuncCall(LINE_FILE, "__str__")
        block: ast.BlockStmt = ast.BlockStmt(LINE_FILE)
        fc.args = block
        func: Function = v.env.get("__str__", LINE_FILE)
        result: lib.String = call_function(fc, func, v.env, None)
        return result
    else:
        return lib.String(v)


def typeof(obj) -> lib.String:
    if obj is None:
        return lib.String("void")
    elif isinstance(obj, ClassInstance):
        return lib.String(obj.class_name)
    elif isinstance(obj, bool):
        return lib.String("boolean")
    elif isinstance(obj, lib.NativeType):
        return lib.String(obj.type_name())
    else:
        t = type(obj)
        return lib.String(t.__name__)


def eval_(expr: lib.String):
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
    lst = lib.List()
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
        for nt in lib.NativeType.__subclasses__():
            if nt.type_name(nt) == obj.name:
                lst.extend(dir(nt))
    elif isinstance(obj, lib.NativeType):
        for nt in lib.NativeType.__subclasses__():
            if nt.type_name(nt) == obj.type_name():
                lst.extend(dir(nt))
    lst.sort()
    return lst


def getcwf(env: Environment):
    return lib.String(env.get_heap("cwf"))


def is_main(env: Environment):
    return env.get_heap("system").argv[0] == getcwf(env)


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
            return to_str(self).literal
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
        raise lib.SplException("Unknown type for for-each loop invariant")
    target = con.lines[1]
    # print(target)
    iterable = evaluate(target, title_scope)
    if isinstance(iterable, lib.Iterable):
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
        ite.args = ast.BlockStmt(LINE_FILE)
        iterator: ClassInstance = evaluate(ite, iterable.env)
        result = None
        while not title_scope.broken:
            block_scope.invalidate()
            nex = ast.FuncCall(lf, "__next__")
            nex.args = ast.BlockStmt(LINE_FILE)
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
        raise lib.SplException(
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
                    return result
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
            raise lib.SplException("Unknown variable level")
        return value
    elif t == ast.DOT:
        if node.level == ast.CONST:
            raise lib.SplException("Unsolved syntax: assigning a constant to an instance")
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
        raise lib.InterpretException("Unknown assignment, in {}, at line {}".format(node.file, node.line_num))


def init_class(node: ast.ClassInit, env: Environment):
    cla: Class = env.get_heap(node.class_name)

    if cla.abstract:
        raise lib.SplException("Abstract class is not instantiable")

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
        kwargs = {}
        for i in range(len(node.args.lines)):
            arg = node.args.lines[i]
            if isinstance(arg, ast.AssignmentNode):
                kwargs[evaluate(arg.left, env)] = evaluate(arg.right, env)
            else:
                args.append(evaluate(arg, env))
        result = func.call(args, kwargs)
        if isinstance(result, ast.BlockStmt):
            # Special case for "eval"
            res = evaluate(result, env)
            return res
        else:
            return result
    else:
        raise lib.InterpretException("Not a function call, in {}, at line {}.".format(node.file, node.line_num))


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
        raise lib.AbstractMethodException("Abstract method is not callable, in '{}', at line {}."
                                          .format(call.file, call.line_num))

    scope = Environment(FUNCTION_SCOPE, func.outer_scope)
    scope.scope_name = "Function scope<{}>".format(call.f_name)

    params = func.params

    if call.args is None:
        raise lib.SplException("Argument of  function '{}' not set, in file '{}', at line {}."
                               .format(call.f_name, call.file, call.line_num))
    args = call.args.lines

    pos_args = []  # Positional arguments
    kwargs = {}  # Keyword arguments

    for arg in args:
        if isinstance(arg, ast.Node):
            if arg.node_type == ast.ASSIGNMENT_NODE:
                arg: ast.AssignmentNode
                kwargs[arg.left.name] = arg.right
            elif arg.node_type == ast.UNPACK_OPERATOR:
                arg: ast.UnpackOperator
                args_list: lib.List = call_env.get(arg.value.name, LINE_FILE)
                for an_arg in args_list:
                    pos_args.append(an_arg)
            elif arg.node_type == ast.KW_UNPACK_OPERATOR:
                arg: ast.KwUnpackOperator
                args_pair: lib.Pair = call_env.get(arg.value.name, LINE_FILE)
                # print(args_pair)
                for an_arg in args_pair:
                    kwargs[an_arg.literal] = args_pair[an_arg]
            else:
                pos_args.append(arg)
        else:
            pos_args.append(arg)
    # print(pos_args)
    # print(kwargs)
    # if len(pos_args) + len(kwargs) > len(params):
    #     raise lib.ArgumentException("Too many arguments for function '{}', in file '{}', at line {}"
    #                                 .format(call.f_name, call.file, call.line_num))
    arg_index = 0
    for i in range(len(params)):
        # Assign function arguments
        param: ParameterPair = params[i]
        if param.preset is UNPACK_ARGUMENT:
            arg_index = call_unpack(param.name, pos_args, arg_index, scope, call_env, lf)
            continue
        elif param.preset is KW_UNPACK_ARGUMENT:
            call_kw_unpack(param.name, kwargs, scope, call_env, lf)
            continue
        elif i < len(pos_args):
            arg = pos_args[arg_index]
            arg_index += 1
        elif param.name in kwargs:
            arg = kwargs[param.name]
        elif param.preset is not INVALID:
            arg = param.preset
        else:
            raise lib.ArgumentException("Function '{}' missing a positional argument '{}', in file '{}', at line {}"
                                        .format(call.f_name, param.name, call.file, call.line_num))

        e = evaluate(arg, call_env)
        scope.define_var(param.name, e, lf)

    result = evaluate(func.body, scope)
    func_parent_env.assign("=>", result, lf)
    return result


def call_unpack(name: str, pos_args: list, index, scope: Environment, call_env: Environment, lf) -> int:
    lst = lib.List()
    while index < len(pos_args):
        arg = pos_args[index]
        e = evaluate(arg, call_env)
        lst.append(e)
        index += 1

    scope.define_var(name, lst, lf)
    return index


def call_kw_unpack(name: str, kwargs: dict, scope: Environment, call_env: Environment, lf):
    pair = lib.Pair()
    for k in kwargs:
        v = kwargs[k]
        e = evaluate(v, call_env)
        pair[lib.String(k)] = e

    scope.define_var(name, pair, lf)


def eval_dot(node: ast.Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.node_type
    # print(node.left)
    if t == ast.NAME_NODE:
        obj: ast.NameNode
        if obj.name == "this":
            raise lib.UnauthorizedException("Access 'this' from outside")
        if isinstance(instance, lib.NativeType):
            return native_types_invoke(instance, obj)
        elif isinstance(instance, ClassInstance):
            attr = instance.env.get(obj.name, (node.line_num, node.file))
            return attr
        else:
            raise lib.InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    elif t == ast.FUNCTION_CALL:
        obj: ast.FuncCall
        if isinstance(instance, lib.NativeType):
            try:
                return native_types_call(instance, obj, env)
            except IndexError as ie:
                raise lib.IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
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
            raise lib.InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    else:
        raise lib.InterpretException("Unknown Syntax, in {}, at line {}".format(node.file, node.line_num))


def arithmetic(left, right_node: ast.Node, symbol, env: Environment):
    if symbol in stl.LAZY:
        if left is None or isinstance(left, bool):
            return primitive_and_or(left, right_node, symbol, env)
        elif isinstance(left, int) or isinstance(left, float):
            return num_and_or(left, right_node, symbol, env)
        else:
            raise lib.InterpretException("Operator '||' '&&' do not support type.")
    else:
        right = evaluate(right_node, env)
        if left is None or isinstance(left, bool):
            return primitive_arithmetic(left, right, symbol)
        elif isinstance(left, int) or isinstance(left, float):
            return num_arithmetic(left, right, symbol)
        elif isinstance(left, lib.String):
            return string_arithmetic(left, right, symbol)
        elif isinstance(left, ClassInstance):
            return instance_arithmetic(left, right, symbol, env, right_node)
        else:
            return raw_type_comparison(left, right, symbol)


def instance_arithmetic(left: ClassInstance, right, symbol, env: Environment, right_node):
    if symbol == "===" or symbol == "is":
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


STRING_ARITHMETIC_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "+": lambda left, right: left + right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and right.name == "string"
}


def string_arithmetic(left, right, symbol):
    return STRING_ARITHMETIC_TABLE[symbol](left, right)


RAW_TYPE_COMPARISON_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: False
}


def raw_type_comparison(left, right, symbol):
    return RAW_TYPE_COMPARISON_TABLE[symbol](left, right)


def primitive_and_or(left, right_node: ast.Node, symbol, env: Environment):
    if left:
        if symbol == "&&" or symbol == "and":
            right = evaluate(right_node, env)
            return right
        elif symbol == "||" or symbol == "or":
            return True
        else:
            raise lib.TypeException("Unsupported operation for primitive type")
    else:
        if symbol == "&&" or symbol == "and":
            return False
        elif symbol == "||" or symbol == "or":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("Unsupported operation for primitive type")


PRIMITIVE_ARITHMETIC_TABLE = {
    "==": lambda left, right: left == right,
    "!=": lambda left, right: left != right,
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and PRIMITIVE_FUNC_TABLE[right.name] == type(
        left).__name__
}


def primitive_arithmetic(left, right, symbol):
    operation = PRIMITIVE_ARITHMETIC_TABLE[symbol]
    return operation(left, right)


def num_and_or(left, right_node: ast.Node, symbol, env: Environment):
    if left:
        if symbol == "||" or symbol == "or":
            return True
        elif symbol == "&&" or symbol == "and":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("No such symbol")
    else:
        if symbol == "&&" or symbol == "and":
            return False
        elif symbol == "||" or symbol == "or":
            right = evaluate(right_node, env)
            return right
        else:
            raise lib.TypeException("No such symbol")


def divide(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return a // b
    else:
        return a / b


NUMBER_ARITHMETIC_TABLE = {
    "+": lambda left, right: left + right,
    "-": lambda left, right: left - right,
    "*": lambda left, right: left * right,
    "/": divide,  # a special case in case to produce integer if int/int
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
    "===": lambda left, right: left is right,
    "is": lambda left, right: left is right,
    "!==": lambda left, right: left is not right,
    "instanceof": lambda left, right: isinstance(right, NativeFunction) and right.name == type(left).__name__
}


def num_arithmetic(left, right, symbol):
    return NUMBER_ARITHMETIC_TABLE[symbol](left, right)


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


def native_types_call(instance: lib.NativeType, method: ast.FuncCall, env: Environment):
    """
    Calls a method of a native object.

    :param instance: the NativeType object instance
    :param method: the method being called
    :param env: the current working environment
    :return: the returning value of the method called
    """
    args = []
    for x in method.args.lines:
        args.append(evaluate(x, env))
    name = method.f_name
    type_ = type(instance)
    method = getattr(type_, name)
    params: tuple = method.__code__.co_varnames
    if "env" in params and params.index("env") == 1:
        res = method(instance, env, *args)
    else:
        res = method(instance, *args)
    return res


def native_types_invoke(instance: lib.NativeType, node: ast.NameNode):
    """
    Invokes an attribute of a native type.

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
        raise lib.InterpretException("Unknown boolean value")


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
        raise lib.ArgumentException("Wrong argument number for 'for' loop, in {}, at line {}"
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
        elif p.node_type == ast.UNPACK_OPERATOR:
            p: ast.UnpackOperator
            name = p.value.name
            value = UNPACK_ARGUMENT
        elif p.node_type == ast.KW_UNPACK_OPERATOR:
            p: ast.KwUnpackOperator
            name = p.value.name
            value = KW_UNPACK_ARGUMENT
        else:
            raise lib.SplException("Unexpected syntax in function parameter, in file '{}', at line {}."
                                   .format(node.file, node.line_num))
        pair = ParameterPair(name, value)
        params_lst.append(pair)

    f = Function(params_lst, node.body, env, node.abstract)
    f.file = node.file
    f.line_num = node.line_num
    options = {"override": "Override" in node.tags, "suppress": "Suppress" in node.tags}
    env.define_function(node.name, f, (node.line_num, node.file), options)

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


def eval_assert(node: ast.AssertStmt, env: Environment):
    result = evaluate(node.value, env)
    if result is not True:
        raise lib.AssertionException("Assertion failed, in file '{}', at line {}".format(node.file, node.line_num))


def raise_exception(e: Exception):
    raise e


# Set of types that will not change after being evaluated
SELF_RETURN_TABLE = {int, float, bool, lib.String, lib.List, lib.Set, lib.Pair, lib.System, lib.File, ClassInstance}

# Operation table of every non-abstract node types
NODE_TABLE = {
    ast.INT_NODE: lambda n, env: n.value,
    ast.FLOAT_NODE: lambda n, env: n.value,
    ast.LITERAL_NODE: lambda n, env: lib.String(n.literal),
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
    ast.THROW_STMT: lambda n, env: raise_exception(RuntimeException(evaluate(n.value, env))),
    ast.TRY_STMT: eval_try_catch,
    ast.JUMP_NODE: eval_jump,
    ast.UNDEFINED_NODE: lambda n, env: UNDEFINED,
    ast.ASSERT_STMT: eval_assert
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
    env.add_heap("cwf", node.file)
    return tn(node, env)

# Processes before run
