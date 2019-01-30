from spl_parser import *
from spl_lib import *


class Interpreter:
    """
    :type ast: Node
    """

    def __init__(self, ast):
        self.ast = ast
        self.env = Environment(True, HashMap())

    def interpret(self):
        return evaluate(self.ast, self.env)


class Environment:
    def __init__(self, is_global, heap):
        self.is_global = is_global
        self.heap = heap  # Heap-allocated variables (global)
        self.variables = HashMap()  # Stack variables

        if is_global:
            self._add_natives()

    def _add_natives(self):
        self.heap["print"] = NativeFunction(print)
        self.heap["time"] = NativeFunction(time)

    def assign(self, key, value):
        # print("assigned {} to {}".format(key, value))
        if self.is_global:
            self.heap[key] = value
        else:
            self.variables[key] = value

    def get(self, key):
        if key in self.variables:
            return self.variables[key]
        else:
            return self.heap[key]


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
    """

    def __init__(self, params, body):
        # self.name = f_name
        self.params = params
        self.body = body

    def __str__(self):
        return "Function<{}>".format(id(self))

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
    if isinstance(node, NumNode):
        return int(node.value)
    elif isinstance(node, NameNode):
        value = env.get(node.name)
        return value
    elif isinstance(node, AssignmentNode):
        key = node.left.name
        value = evaluate(node.right, env)
        env.assign(key, value)
        return value
    elif isinstance(node, OperatorNode):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        symbol = node.operation
        if symbol == "+":
            return int(left) + int(right)
        elif symbol == "-":
            return int(left) - int(right)
        elif symbol == "*":
            return int(left) * int(right)
        elif symbol == "/":
            return int(left) // int(right)
        elif symbol == "%":
            return int(left) % int(right)
        elif symbol == "==":
            return int(left) == int(right)
        elif symbol == "!=":
            return int(left) != int(right)
        elif symbol == ">":
            return int(left) > int(right)
        elif symbol == "<":
            return int(left) < int(right)
        elif symbol == ">=":
            return int(left) >= int(right)
        elif symbol == "<=":
            return int(left) <= int(right)

        raise InterpretException("No such symbol")
    elif isinstance(node, BlockStmt):
        result = 0
        for line in node.lines:
            result = evaluate(line, env)
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
        while evaluate(node.condition, env):
            result = evaluate(node.body, env)
        return result
    elif isinstance(node, DefStmt):
        f = Function(node.params, node.body)
        env.assign(node.name, f)
        return 0
    elif isinstance(node, FuncCall):
        func = env.get(node.f_name)
        if isinstance(func, Function):
            scope = Environment(False, env.heap)
            for i in range(len(func.params)):
                scope.assign(func.params[i].name, evaluate(node.args[i], env))
            # scope.variables.merge(env.variables)
            # print(scope.variables)
            # print(id(scope))
            result = evaluate(func.body, scope)
            return result
        elif isinstance(func, NativeFunction):
            args = []
            for i in range(len(node.args)):
                args.append(evaluate(node.args[i], env))
            return func.call(args)
        else:
            raise InterpretException("Not a function call")

    return None


class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
