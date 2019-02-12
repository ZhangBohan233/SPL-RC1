from spl_parser import *
from spl_lib import *
from spl_lexer import BINARY_OPERATORS

DEBUG = False

ID_COUNTER = Counter()

LST = [72, 97, 112, 112, 121, 32, 66, 105, 114, 116, 104, 100, 97, 121, 32,
       73, 115, 97, 98, 101, 108, 108, 97, 33, 33, 33]


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

    def set_ast(self, ast: BlockStmt):
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
            self._add_base_exception()

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

        self.add_heap("boolean", NativeFunction(to_boolean, "boolean"))
        self.add_heap("void", NativeFunction(None, "void"))

    def _add_base_exception(self):
        loc = (0, "interpreter")

        constructor = DefStmt(loc, "Exception", lex.PUBLIC)
        constructor.params = [NameNode(loc, "msg", lex.PUBLIC)]
        constructor.presets = [LiteralNode(loc, "")]

        c_body = BlockStmt(loc)
        asg = AssignmentNode(loc)
        asg.left = NameNode(loc, "message", lex.PUBLIC)
        asg.right = NameNode(loc, "msg", lex.PUBLIC)
        c_body.lines.append(asg)

        constructor.body = c_body

        body = BlockStmt(loc)

        asg2 = AssignmentNode(loc)
        asg2.left = NameNode(loc, "message", lex.PUBLIC)
        asg2.right = LiteralNode(loc, "")

        body.lines.append(asg2)
        body.lines.append(constructor)
        exception = Class("Exception", body)
        self.add_heap("Exception", exception)

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
        if DEBUG:
            print("assigned {} to {}".format(key, value))
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
    def __init__(self, func: callable, name: str):
        self.name = name
        self.function = func

    def __str__(self):
        return "NativeFunction {}".format(self.function.__name__)

    def __repr__(self):
        return self.__str__()

    def call(self, args):
        return self.function(*args)


class Function:
    """
    :type body: BlockStmt
    :type outer_scope: Environment
    """

    def __init__(self, params, presets, body):
        # self.name = f_name
        self.params = params
        self.presets = presets
        self.body = body
        self.outer_scope = None

    def __str__(self):
        return "Function<{}>".format(id(self))

    def __repr__(self):
        return self.__str__()


class Class:
    def __init__(self, class_name: str, body: BlockStmt):
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


class ClassInstance:
    def __init__(self, env: Environment, class_name: str):
        """
        ===== Attributes =====
        :param class_name: name of this class
        :param env: instance attributes
        """
        self.class_name = class_name
        self.env = env
        self.env.variables["id"] = ID_COUNTER.get()
        ID_COUNTER.increment()
        self.env.variables["this"] = self

    def __hash__(self):
        if self.env.contains_key("__hash__"):
            call = FuncCall((0, "interpreter"), "__hash__")
            call.args = []
            return evaluate(call, self.env)
        else:
            return hash(self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.env.contains_key("__str__"):
            call = FuncCall((0, "interpreter"), "__str__")
            call.args = []
            return str(evaluate(call, self.env))
        else:
            return self.class_name + ": " + str(self.env.variables)
        # return bytes(LST).decode("ascii")


class RuntimeException(SplException):
    def __init__(self, exception: ClassInstance):
        SplException.__init__(self, "RuntimeException")

        self.exception = exception


def evaluate(node: Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding working environment.

    :param node: the node in abstract syntax tree to be evaluated
    :param env: the working environment
    :return: the evaluation result
    """
    if node is None:
        return NULL
    elif node == NULL:
        return NULL
    elif env.terminated:
        return env.exit_value
    elif env.paused:
        return NULL
    elif isinstance(node, Node):
        t = node.type
        if t == INT_NODE:
            node: IntNode
            return node.value
        elif t == FLOAT_NODE:
            node: FloatNode
            return node.value
        elif t == LITERAL_NODE:
            node: LiteralNode
            # s = node.literal
            s = node.literal
            return String(s)
        elif t == NAME_NODE:
            node: NameNode
            value = env.get(node.name, (node.line_num, node.file))
            return value
        elif t == BOOLEAN_STMT:
            node: BooleanStmt
            if node.value in {"true", "false"}:
                return get_boolean(node.value == "true")
            else:
                raise InterpretException("Unknown boolean value")
        elif t == NULL_STMT:
            return NULL
        elif t == BREAK_STMT:
            env.break_loop()
        elif isinstance(node, ContinueStmt):
            env.pause_loop()
        elif isinstance(node, AssignmentNode):
            return assignment(node, env)
        elif isinstance(node, Dot):
            return call_dot(node, env)
        elif isinstance(node, AnonymousCall):
            evaluate(node.left, env)
            right = node.right.args
            fc = FuncCall((node.line_num, node.file), "=>")
            fc.args = right
            return evaluate(fc, env)
        elif t == OPERATOR_NODE:
            node: OperatorNode
            return eval_operator(node, env)
        elif t == NEGATIVE_EXPR:
            node: NegativeExpr
            value = evaluate(node.value, env)
            return -value
        elif t == NOT_EXPR:
            node: NotExpr
            value = evaluate(node.value, env)
            if value:
                return FALSE
            else:
                return TRUE
        elif t == RETURN_STMT:
            node: ReturnStmt
            value = node.value
            res = evaluate(value, env)
            # print(env.variables)
            env.terminate(res)
            return res
        elif t == BLOCK_STMT:
            node: BlockStmt
            result = 0
            for line in node.lines:
                result = evaluate(line, env)
            return result
        elif t == IF_STMT:
            node: IfStmt
            cond = evaluate(node.condition, env)
            if cond:
                return evaluate(node.then_block, env)
            else:
                return evaluate(node.else_block, env)
        elif t == WHILE_STMT:
            node: WhileStmt
            result = 0
            while not env.broken and evaluate(node.condition, env):
                result = evaluate(node.body, env)
                env.paused = False  # reset the environment the the next iteration
            env.broken = False  # reset the environment for next loop
            return result
        elif t == FOR_LOOP_STMT:
            node: ForLoopStmt
            con: BlockStmt = node.condition
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
        elif t == DEF_STMT:
            node: DefStmt
            f = Function(node.params, node.presets, node.body)
            f.outer_scope = env
            env.assign(node.name, f)
            if node.auth == lex.PRIVATE:
                env.add_private(node.name)
            return f
        elif t == FUNCTION_CALL:
            node: FuncCall
            return call_function(node, env)
        elif t == CLASS_STMT:
            node: ClassStmt
            cla = Class(node.class_name, node.block)
            cla.superclass_names = node.superclass_names
            env.assign(node.class_name, cla)
            return cla
        elif t == CLASS_INIT:
            node: ClassInit
            return init_class(node, env)
        elif t == INVALID_TOKEN:
            raise InterpretException("Non-default argument follows default argument, in {}, at line {}"
                                     .format(node.file, node.line_num))
        elif t == ABSTRACT:
            raise AbstractMethodException("Method is not implemented, in {}, at line {}"
                                          .format(node.file, node.line_num))
        elif t == THROW_STMT:
            node: ThrowStmt
            raise RuntimeException(evaluate(node.value, env))
        elif t == TRY_STMT:
            node: TryStmt
            return eval_try_catch(node, env)
        else:
            raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))
    elif isinstance(node, int) or isinstance(node, float) or isinstance(node, NativeType):
        return node
    else:
        raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))


def eval_try_catch(node: TryStmt, env: Environment):
    try:
        return evaluate(node.try_block, env)
    except RuntimeException as re:
        exception: ClassInstance = re.exception
        exception_class = env.get_class(exception.class_name)
        catches = node.catch_blocks
        for cat in catches:
            for line in cat.condition.lines:
                catch_name = line.right.name
                # exception_name = exception.class_name
                if is_subclass_of(exception_class, catch_name, env):
                    return evaluate(cat.then, env)
        raise re
    finally:
        if node.finally_block:
            return evaluate(node.finally_block, env)


def is_subclass_of(child_class: Class, class_name: str, env: Environment) -> bool:
    if child_class.class_name == class_name:
        return True
    else:
        return any([is_subclass_of(env.get_class(ccn), class_name, env) for ccn in child_class.superclass_names])


def eval_operator(node: OperatorNode, env: Environment):
    left = evaluate(node.left, env)
    right = evaluate(node.right, env)
    if node.assignment:
        symbol = node.operation[:-1]
        res = arithmetic(left, right, symbol, env)
        asg = AssignmentNode((node.line_num, node.file))
        asg.left = node.left
        asg.operation = "="
        asg.right = res
        return evaluate(asg, env)
    else:
        symbol = node.operation
        return arithmetic(left, right, symbol, env)


def assignment(node: AssignmentNode, env: Environment):
    key = node.left
    value = evaluate(node.right, env)
    t = key.type
    if t == NAME_NODE:
        env.assign(key.name, value)
        if key.auth == lex.PRIVATE:
            env.add_private(key.name)
        return value
    elif t == DOT:
        node = key
        name_lst = []
        while isinstance(node, Dot):
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


def init_class(node: ClassInit, env: Environment):
    cla: Class = env.get_class(node.class_name)

    scope = Environment(False, env.heap)
    scope.scope_name = "Class scope<{}>".format(cla.class_name)
    class_inheritance(cla, env, scope)

    # print(scope.variables)
    instance = ClassInstance(scope, node.class_name)
    for k in scope.variables:
        v = scope.variables[k]
        if isinstance(v, Function):
            # v.parent = instance
            v.outer_scope = scope

    if node.args:
        # constructor: Function = scope.variables[node.class_name]
        fc = FuncCall((node.line_num, node.file), node.class_name)
        fc.args = node.args
        for a in fc.args.lines:
            scope.temp_vars.append(evaluate(a, env))
        # print(scope.variables)
        evaluate(fc, scope)
    # if cla.class_name == "Exception":
    #     return instance.env.get("message", (0, "interpreter"))
    # else:
    return instance


def call_function(node: FuncCall, env: Environment):
    func = env.get(node.f_name, (node.line_num, node.file))
    if isinstance(func, Function):
        scope = Environment(False, env.heap)
        scope.scope_name = "Function scope<{}>".format(node.f_name)
        scope.outer = func.outer_scope  # supports for closure

        if len(env.temp_vars) == len(func.params):
            for i in range(len(func.params)):
                scope.assign(func.params[i].name, env.temp_vars[i])
            env.temp_vars.clear()
        else:
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
        if isinstance(result, BlockStmt):
            # Special case for "eval"
            r = evaluate(result, env)
            return r
        else:
            return result
    else:
        raise InterpretException("Not a function call")


def call_dot(node: Dot, env: Environment):
    instance = evaluate(node.left, env)
    obj = node.right
    t = obj.type
    if t == NAME_NODE:
        if isinstance(instance, NativeType):
            return native_types_invoke(instance, obj)
        elif isinstance(instance, ClassInstance):
            if instance.env.is_private(obj.name):
                raise UnauthorizedException("Class attribute {} has private access".format(obj.name))
            else:
                attr = instance.env.variables[obj.name]
                return attr
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    elif t == FUNCTION_CALL:
        if isinstance(instance, NativeType):
            try:
                return native_types_call(instance, obj, env)
            except IndexError as ie:
                raise IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                               .format(node.file, node.line_num))
        elif isinstance(instance, ClassInstance):
            if instance.env.is_private(obj.f_name):
                raise UnauthorizedException("Class attribute {} has private access".format(obj.f_name))
            else:
                result = evaluate(obj, instance.env)
                env.assign("=>", result)
                return result
        else:
            raise InterpretException("Not a class instance, in {}, at line {}".format(node.file, node.line_num))
    else:
        raise InterpretException("Unknown Syntax")


def arithmetic(left, right, symbol, env: Environment):
    if isinstance(left, int) or isinstance(left, float):
        return num_arithmetic(left, right, symbol)
    elif isinstance(left, String):
        return string_arithmetic(left, right, symbol)
    elif isinstance(left, Primitive):
        return primitive_arithmetic(left, right, symbol)
    elif isinstance(left, ClassInstance):
        return instance_arithmetic(left, right, symbol, env)
    else:
        return raw_type_comparison(left, right, symbol)


def instance_arithmetic(left: ClassInstance, right, symbol, env: Environment):
    if symbol == "===":
        return TRUE if isinstance(right, ClassInstance) and \
                       left.env.variables["id"] == right.env.variables["id"] else FALSE
    elif symbol == "!==":
        return TRUE if not isinstance(right, ClassInstance) or \
                       left.env.variables["id"] != right.env.variables["id"] else FALSE
    elif symbol == "instanceof":
        if isinstance(right, Class):
            return TRUE if is_subclass_of(env.get_class(left.class_name), right.class_name, env) else FALSE
        else:
            return FALSE
    else:
        fc = FuncCall((0, "interpreter"), "@" + BINARY_OPERATORS[symbol])
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
        if isinstance(right, NativeFunction) and right.name == "string":
            return TRUE
        else:
            return FALSE
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
            return TRUE if type(left).__name__ == right.literal else FALSE
        else:
            return FALSE
    else:
        raise InterpretException("Unsupported operation for raw type " + left.type_name())

    return get_boolean(result)


def primitive_arithmetic(left: Primitive, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == "&&":
        result = left and right
    elif symbol == "||":
        result = left or right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction) and right.name == left.type_name():
            return TRUE
        else:
            return FALSE
    else:
        raise InterpretException("Unsupported operation for primitive type " + left.type_name())

    return get_boolean(result)


def num_arithmetic(left, right, symbol):
    if symbol == "+":
        result = left + right
    elif symbol == "-":
        result = left - right
    elif symbol == "*":
        result = left * right
    elif symbol == "/":
        result = left / right
    elif symbol == "%":
        result = left % right
    elif symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
    elif symbol == ">":
        result = left > right
    elif symbol == "<":
        result = left < right
    elif symbol == ">=":
        result = left >= right
    elif symbol == "<=":
        result = left <= right
    elif symbol == "&&":
        result = left and right
    elif symbol == "||":
        result = left or right
    elif symbol == "<<":
        result = left << right
    elif symbol == ">>":
        result = left >> right
    elif symbol == "&":
        result = left & right
    elif symbol == "^":
        result = left ^ right
    elif symbol == "|":
        result = left | right
    elif symbol == "===":
        result = left == right
    elif symbol == "!==":
        result = left != right
    elif symbol == "instanceof":
        if isinstance(right, NativeFunction) and right.name == type(left).__name__:
            return TRUE
        else:
            return FALSE
    else:
        raise InterpretException("No such symbol")

    if isinstance(result, bool):
        return get_boolean(result)
    else:
        return result


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
        class_inheritance(env.get_class(sc), env, scope)

    evaluate(cla.body, scope)  # this step just fills the scope


def native_types_call(instance, method, env):
    """

    :param instance:
    :type instance: NativeType
    :param method:
    :type method: FuncCall
    :type env: Environment
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


def native_types_invoke(instance: NativeType, node: NameNode):
    """

    :param instance:
    :param node:
    :return:
    """
    name = node.name
    type_ = type(instance)
    res = getattr(type_, name)
    return res


def get_boolean(expr):
    if expr:
        return TRUE
    else:
        return FALSE
