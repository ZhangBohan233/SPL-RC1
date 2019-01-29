from spl_parser import *
from spl_lib import *


class Interpreter:
    """
    :type ast: Node
    """
    def __init__(self, ast):
        self.ast = ast
        self.env = Environment()

    def interpret(self):
        return evaluate(self.ast, self.env)


class Environment:
    def __init__(self, heap=HashMap()):
        self.heap = heap
        self.variables = HashMap()
        # self.calls = Stack()

    def assign(self, key, value):
        self.variables[key] = value

    def get(self, key):
        return self.variables[key]


class Function:
    """
    :type body: BlockStmt
    """
    def __init__(self, f_name, params, body):
        self.name = f_name
        self.params = params
        self.body = body

    def __str__(self):
        return "Function<{} at {}>".format(self.name, id(self))

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
        f = Function(node.name, node.params, node.body)
        env.assign(node.name, f)
        return 0
    elif isinstance(node, FuncCall):
        func: Function = env.get(node.f_name)
        scope = Environment(env.heap)
        for i in range(len(func.params)):
            scope.assign(func.params[i].name, evaluate(node.args[i], env))
        # scope.variables.merge(env.variables)
        print(scope.variables)
        return evaluate(func.body, scope)

    return None


class InterpretException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
