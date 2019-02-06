from spl_parser import *
from spl_lib import *
from spl_lexer import BINARY_OPERATORS

DEBUG = False


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    """

    def __init__(self, argv):
        self.ast = None
        self.argv = argv
        self.env = Environment(True, HashMap())
        self.env.heap["system"] = System(argv)
        self.env.scope_name = "Global"

    def set_ast(self, ast):
        self.ast = ast

    def interpret(self):
        return evaluate(self.ast, self.env)


class Environment:
    """
    ===== Attributes =====
    :type outer: Environment
    """

    def __init__(self, is_global, heap):
        self.is_global = is_global
        self.heap = heap  # Heap-allocated variables (global)
        self.variables = HashMap()  # Stack variables
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

    def __str__(self):
        if self.scope_name:
            return self.scope_name
        else:
            return str(super)

    def _add_natives(self):
        self.heap["print"] = NativeFunction(print_)
        self.heap["time"] = NativeFunction(time)
        self.heap["type"] = NativeFunction(typeof)
        self.heap["list"] = NativeFunction(make_list)
        self.heap["pair"] = NativeFunction(make_pair)
        self.heap["int"] = NativeFunction(to_int)
        self.heap["float"] = NativeFunction(to_float)

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

    def get(self, key: str, line_num):
        if key in self.variables:
            return self.variables[key]
        elif self.outer:
            return self.outer.get(key, line_num)
        else:
            if key in self.heap:
                return self.heap[key]
            else:
                raise SplException("Usage before assignment for name '{}', at line {}".format(key, line_num))

    def get_class(self, classname):
        return self.heap[classname]


class NativeFunction:
    def __init__(self, func):
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
    def __init__(self, class_name, body):
        self.class_name = class_name
        self.body = body
        self.superclass_name = None

    def __str__(self):
        if self.superclass_name:
            return "Class<> extends " + self.superclass_name
        else:
            return "Class<>"

    def __repr__(self):
        return self.__str__()


class ClassInstance:
    def __init__(self, env, classname):
        """
        :type env: Environment
        """
        self.classname = classname
        self.env = env

    def __str__(self):
        return self.classname + ": " + str(self.env.variables)

    def __repr__(self):
        return self.__str__()


def evaluate(node: Node, env: Environment):
    """
    Evaluates a abstract syntax tree node, with the corresponding worrking environment.

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
    elif isinstance(node, IntNode):
        return int(node.value)
    elif isinstance(node, FloatNode):
        return float(node.value)
    elif isinstance(node, LiteralNode):
        return String(node.literal)
    elif isinstance(node, NameNode):
        value = env.get(node.name, node.line_num)
        return value
    elif isinstance(node, BooleanStmt):
        if node.value in {"true", "false"}:
            return get_boolean(node.value == "true")
        else:
            raise InterpretException("Unknown boolean value")
    elif isinstance(node, NullStmt):
        return NULL
    elif isinstance(node, BreakStmt):
        env.break_loop()
    elif isinstance(node, ContinueStmt):
        env.pause_loop()
    elif isinstance(node, AssignmentNode):
        key = node.left
        value = evaluate(node.right, env)
        if isinstance(key, NameNode):
            env.assign(key.name, value)
            return value
        elif isinstance(key, Dot):
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
                scope = scope.get(t, node.line_num).env
            scope.assign(name_lst[-1], value)
            return value
    elif isinstance(node, Dot):
        instance = evaluate(node.left, env)
        obj = node.right
        if isinstance(obj, NameNode):
            if isinstance(instance, NativeTypes):
                return native_types_invoke(instance, obj)
            elif isinstance(instance, ClassInstance):
                attr = instance.env.variables[obj.name]
                return attr
            else:
                raise InterpretException("Not a class instance")
        elif isinstance(obj, FuncCall):
            if isinstance(instance, NativeTypes):
                try:
                    return native_types_call(instance, obj, env)
                except IndexError as ie:
                    raise IndexOutOfRangeException(str(ie) + " in file: '{}', at line {}"
                                                   .format(node.file, node.line_num))
            elif isinstance(instance, ClassInstance):
                return evaluate(obj, instance.env)
            else:
                raise InterpretException("Not a class instance")
        else:
            raise InterpretException("Unknown Syntax")
    elif isinstance(node, OperatorNode):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        if node.assignment:
            symbol = node.operation[:-1]
            res = arithmetic(left, right, symbol)
            asg = AssignmentNode((node.line_num, node.file))
            asg.left = node.left
            asg.operation = "="
            asg.right = res
            return evaluate(asg, env)
        else:
            symbol = node.operation
            return arithmetic(left, right, symbol)
    elif isinstance(node, NegativeExpr):
        value = evaluate(node.value, env)
        return -value
    elif isinstance(node, NotExpr):
        value = evaluate(node.value, env)
        if value:
            return FALSE
        else:
            return TRUE
    elif isinstance(node, ReturnStmt):
        value = node.value
        res = evaluate(value, env)
        # print(env.variables)
        env.terminate(res)
        return res
    elif isinstance(node, BlockStmt):
        result = 0
        for line in node.lines:
            result = evaluate(line, env)
            # print(result)
            # print(line)
        return result
    elif isinstance(node, IfStmt):
        cond = evaluate(node.condition, env)
        if cond.value:
            return evaluate(node.then_block, env)
        else:
            return evaluate(node.else_block, env)
    elif isinstance(node, WhileStmt):
        result = 0
        while not env.broken and evaluate(node.condition, env):
            result = evaluate(node.body, env)
            env.paused = False  # reset the environment the the next iteration
        env.broken = False  # reset the environment for next loop
        return result
    elif isinstance(node, ForLoopStmt):
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
    elif isinstance(node, DefStmt):
        f = Function(node.params, node.presets, node.body)
        f.outer_scope = env
        env.assign(node.name, f)
        return f
    elif isinstance(node, FuncCall):
        func = env.get(node.f_name, node.line_num)
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
                    # print(arg)
                    e = evaluate(arg, env)
                    scope.assign(func.params[i].name, e)
            result = evaluate(func.body, scope)
            return result
        elif isinstance(func, NativeFunction):
            args = []
            for i in range(len(node.args.lines)):
                # args.append(evaluate(node.args[i], env))
                args.append(evaluate(node.args.lines[i], env))
            return func.call(args)
        else:
            raise InterpretException("Not a function call")
    elif isinstance(node, ClassStmt):
        cla = Class(node.class_name, node.block)
        cla.superclass_name = node.superclass_name
        env.assign(node.class_name, cla)
        return cla
    elif isinstance(node, ClassInit):
        cla: Class = env.get_class(node.class_name)

        scope = Environment(False, env.heap)
        scope.scope_name = "Class scope<{}>".format(cla.class_name)
        class_inheritance(cla, env, scope)

        # print(scope.variables)
        instance = ClassInstance(scope, node.class_name)
        for k in scope.variables.key_set():
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
        return instance
    elif isinstance(node, int) or isinstance(node, float) or isinstance(node, Null) or isinstance(node, Boolean) or \
            isinstance(node, NativeTypes):
        return node
    else:
        raise InterpretException("Invalid Syntax Tree in {}, at line {}".format(node.file, node.line_num))


def arithmetic(left, right, symbol):
    if isinstance(left, int) or isinstance(left, float):
        return num_arithmetic(left, right, symbol)
    elif isinstance(left, Primitive):
        return primitive_arithmetic(left, right, symbol)
    elif isinstance(left, ClassInstance):
        fc = FuncCall(0, "@" + BINARY_OPERATORS[symbol])
        left.env.temp_vars.append(right)
        res = evaluate(fc, left.env)
        return res
    else:
        return raw_type_comparison(left, right, symbol)


def raw_type_comparison(left, right, symbol):
    if symbol == "==":
        result = left == right
    elif symbol == "!=":
        result = left != right
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
        if isinstance(left, int):
            result = left // right
        else:
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
    if cla.superclass_name:
        class_inheritance(env.get_class(cla.superclass_name), env, scope)

    evaluate(cla.body, scope)


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


def native_types_invoke(instance: NativeTypes, node: NameNode):
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


class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


class SplException(InterpretException):
    def __init__(self, msg=""):
        InterpretException.__init__(self, msg)


class IndexOutOfRangeException(SplException):
    def __init__(self, msg):
        SplException.__init__(self, msg)
