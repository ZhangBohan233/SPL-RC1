from spl_parser import *
from spl_lib import *

DEBUG = False


class Interpreter:
    """
    :type ast: Node
    :type argv: list
    """

    def __init__(self, ast, argv):
        self.ast = ast
        self.argv = argv
        self.env = Environment(True, HashMap())

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

        # environment signals
        self.terminated = False
        self.exit_value = None
        self.broken = False
        self.paused = False
        # self.var_array = []
        # self.heap1 = heap

        if is_global:
            self._add_natives()

    def _add_natives(self):
        self.heap["print"] = NativeFunction(print)
        self.heap["time"] = NativeFunction(time)
        self.heap["type"] = NativeFunction(typeof)

    def terminate(self, exit_value):
        self.terminated = True
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

    def get(self, key):
        if key in self.variables:
            return self.variables[key]
        elif self.outer:
            return self.outer.get(key)
        else:
            return self.heap[key]

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

    def __init__(self, params, body):
        # self.name = f_name
        self.params = params
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


def evaluate(node, env):
    """

    :param node:
    :param env:
    :type node: Node
    :type env: Environment
    :return:
    """
    if not node:
        return None
    elif env.terminated:
        return env.exit_value
    elif env.paused:
        return None
    elif isinstance(node, IntNode):
        return int(node.value)
    elif isinstance(node, FloatNode):
        return float(node.value)
    elif isinstance(node, LiteralNode):
        return node.literal
    elif isinstance(node, NameNode):
        value = env.get(node.name)
        return value
    elif isinstance(node, BooleanStmt):
        if node.value == "true":
            return True
        elif node.value == "false":
            return False
        else:
            raise InterpretException("Unknown boolean value")
    elif isinstance(node, NullStmt):
        return None
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
                scope = scope.get(t).env
            scope.assign(name_lst[-1], value)
            return value
    elif isinstance(node, Dot):
        instance: ClassInstance = evaluate(node.left, env)
        obj = node.right
        if isinstance(obj, NameNode):
            attr = instance.env.variables[obj.name]
            return attr
        elif isinstance(obj, FuncCall):
            # attr = instance.attributes[obj.f_name]
            # print(obj)
            return evaluate(obj, instance.env)
        else:
            raise InterpretException("Unknown Syntax")
    elif isinstance(node, OperatorNode):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        symbol = node.operation
        return arithmetic(left, right, symbol)
    elif isinstance(node, NegativeExpr):
        value = evaluate(node.value, env)
        return -value
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
        if cond:
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
    elif isinstance(node, DefStmt):
        f = Function(node.params, node.body)
        f.outer_scope = env
        env.assign(node.name, f)
        return f
    elif isinstance(node, FuncCall):
        func = env.get(node.f_name)
        if isinstance(func, Function):
            scope = Environment(False, env.heap)
            scope.outer = func.outer_scope  # supports for closure
            # print(scope.variables)
            # print(env.is_global)
            for i in range(len(func.params)):
                # Assign function arguments
                scope.assign(func.params[i].name, evaluate(node.args[i], env))
            result = evaluate(func.body, scope)
            return result
        elif isinstance(func, NativeFunction):
            args = []
            for i in range(len(node.args)):
                args.append(evaluate(node.args[i], env))
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
        class_inheritance(cla, env, scope)

        # print(scope.variables)
        instance = ClassInstance(scope, node.class_name)
        for k in scope.variables.key_set():
            v = scope.variables[k]
            if isinstance(v, Function):
                v.parent = instance

        if node.args:
            # constructor: Function = scope.variables[node.class_name]
            fc = FuncCall(node.class_name)
            fc.args = node.args
            # print(constructor)
            evaluate(fc, scope)
        return instance
    else:
        raise InterpretException("Invalid Syntax Tree")


def arithmetic(left, right, symbol):
    if symbol == "+":
        return left + right
    elif symbol == "-":
        return left - right
    elif symbol == "*":
        return left * right
    elif symbol == "/":
        return left // right
    elif symbol == "%":
        return left % right
    elif symbol == "==":
        return left == right
    elif symbol == "!=":
        return left != right
    elif symbol == ">":
        return left > right
    elif symbol == "<":
        return left < right
    elif symbol == ">=":
        return left >= right
    elif symbol == "<=":
        return left <= right
    elif symbol == "&&":
        return left and right
    elif symbol == "||":
        return left or right
    elif symbol == "<<":
        return left << right
    elif symbol == ">>":
        return left >> right
    elif symbol == "&":
        return left & right
    elif symbol == "^":
        return left ^ right
    elif symbol == "|":
        return left | right

    raise InterpretException("No such symbol")


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
        class_inheritance(env.get(cla.superclass_name), env, scope)

    evaluate(cla.body, scope)


class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
