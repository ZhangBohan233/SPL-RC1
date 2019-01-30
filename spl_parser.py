PRECEDENCE = {"+": 50, "-": 50, "*": 100, "/": 100, "%": 100,
              "==": 10, ">": 10, "<": 10, ">=": 10, "<=": 10, "!=": 10, ".": 500}


class Parser:
    """
    :type inner: Parser
    """

    def __init__(self):
        self.elements = []
        self.stack = []
        self.inner = None

    def __str__(self):
        return str(self.elements)
        # s = "["
        # for x in self.elements:
        #     s += (str(x) + ",\n")
        # return s + "]"

    def add_name(self, n):
        if self.inner:
            self.inner.add_name(n)
        else:
            self.stack.append(NameNode(n))

    def add_number(self, v):
        if self.inner:
            self.inner.add_number(v)
        else:
            self.stack.append(NumNode(v))

    def add_operator(self, op, extra_precedence):
        if self.inner:
            self.inner.add_operator(op, extra_precedence)
        else:
            op_node = OperatorNode(extra_precedence)
            op_node.operation = op
            # left = self.stack.pop()
            # op_node.left = left
            self.stack.append(op_node)

    def add_assignment(self):
        if self.inner:
            self.inner.add_assignment()
        else:
            name = self.stack.pop()
            ass_node = AssignmentNode()
            ass_node.left = name
            ass_node.operation = "="
            self.stack.append(ass_node)

    def add_if(self):
        if self.inner:
            self.inner.add_if()
        else:
            ifs = IfStmt()
            self.stack.append(ifs)

    def add_else(self):
        if self.inner:
            self.inner.add_else()
        else:
            pass
            # node = self.stack.pop()

    def add_while(self):
        if self.inner:
            self.inner.add_while()
        else:
            whs = WhileStmt()
            self.stack.append(whs)

    def add_function(self, f_name):
        if self.inner:
            self.inner.add_function(f_name)
        else:
            func = DefStmt(f_name)
            self.stack.append(func)

    def build_func_params(self, params: list):
        if self.inner:
            self.inner.build_func_params(params)
        else:
            func = self.stack.pop()
            lst = [NameNode(x) for x in params]
            func.params = lst
            self.stack.append(func)

    def add_call(self, f_name):
        if self.inner:
            self.inner.add_call(f_name)
        else:
            fc = FuncCall(f_name)
            self.stack.append(fc)

    def build_call_expr(self):
        if self.inner:
            self.inner.build_call_expr()
        else:
            lst = []
            while not isinstance(self.stack[-1], FuncCall):
                lst.append(self.stack.pop())
            lst.reverse()

            node = parse_expr(lst)
            self.stack.append(node)

    def build_call(self):
        if self.inner:
            self.inner.build_call()
        else:
            lst = []
            while not isinstance(self.stack[-1], FuncCall):
                lst.append(self.stack.pop())

            lst.reverse()
            node = self.stack.pop()
            node.args = lst
            self.stack.append(node)

    def build_condition(self):
        if self.inner:
            self.inner.build_condition()
        else:
            expr = self.stack.pop()
            cond_stmt: CondStmt = self.stack.pop()
            cond_stmt.condition = expr
            self.stack.append(cond_stmt)

    def new_block(self):
        if self.inner:
            self.inner.new_block()
        else:
            self.inner = Parser()

    def add_class(self, class_name):
        if self.inner:
            self.inner.add_class(class_name)
        else:
            cs = ClassStmt(class_name)
            self.stack.append(cs)

    def build_class(self):
        if self.inner:
            self.inner.build_class()
        else:
            node = self.stack.pop()
            class_node = self.stack.pop()
            class_node.block = node
            self.stack.append(class_node)

    def add_class_new(self, class_name):
        if self.inner:
            self.inner.add_class_new(class_name)
        else:
            node = ClassInit(class_name)
            self.stack.append(node)

    def add_dot(self, extra_precedence):
        if self.inner:
            self.inner.add_dot(extra_precedence)
        else:
            node = Dot(extra_precedence)
            self.stack.append(node)

    def build_block(self):
        if self.inner.inner:
            self.inner.build_block()
        else:
            root = self.inner.get_as_block()
            self.inner = None
            self.stack.append(root)

    def build_expr(self):
        if self.inner:
            self.inner.build_expr()
        else:
            lst = []
            # print(self.stack)
            while len(self.stack) > 0:
                node = self.stack.pop()
                if isinstance(node, NumNode) or isinstance(node, NameNode) or isinstance(node, OperatorNode) or \
                        (isinstance(node, FuncCall) and node.args is not None):
                    lst.append(node)
                else:
                    self.stack.append(node)
                    break
            lst.reverse()
            # print(lst)

            node = parse_expr(lst)
            self.stack.append(node)

    def build_line(self):
        if self.inner:
            self.inner.build_line()
        else:
            res = None
            res2 = None
            # print(self.stack)
            while len(self.stack) > 0:
                node = self.stack.pop()
                if isinstance(node, LeafNode):
                    res = node
                elif isinstance(node, BinaryExpr) and res:
                    node.right = res
                    res = node
                elif isinstance(node, BlockStmt):
                    if res:
                        res2 = res
                        res = node
                    else:
                        res = node
                elif isinstance(node, IfStmt):
                    node.then_block = res
                    node.else_block = res2
                    res = node
                elif isinstance(node, WhileStmt):
                    node.body = res
                    res = node
                elif isinstance(node, DefStmt):
                    node.body = res
                    res = node
                else:
                    res = node
            self.elements.append(res)

    def get_as_block(self):
        block = BlockStmt()
        block.lines = self.elements
        return block


class Node:
    def __init__(self):
        pass


class LeafNode(Node):
    def __init__(self):
        Node.__init__(self)


class BinaryExpr(Node):
    """
    :type operation: str
    :type left:
    """

    def __init__(self):
        Node.__init__(self)

        self.left = None
        self.right = None
        self.operation = None

    def __str__(self):
        return "BE({} {} {})".format(self.left, self.operation, self.right)

    def __repr__(self):
        return self.__str__()


class NumNode(LeafNode):
    def __init__(self, v):
        LeafNode.__init__(self)

        self.value = v

    def __str__(self):
        return "Num(" + self.value + ")"

    def __repr__(self):
        return self.__str__()


# class NegativeExpr(Node):
#     def __init__(self):
#         Node.__init__(self)
#
#     def __str__(self):
#         return "-"


class OperatorNode(BinaryExpr):
    def __init__(self, extra):
        BinaryExpr.__init__(self)

        self.extra_precedence = extra * 1000

    def precedence(self):
        return PRECEDENCE[self.operation] + self.extra_precedence


class NameNode(LeafNode):
    def __init__(self, n):
        LeafNode.__init__(self)

        self.name = n
        self.postfix = None

    def __str__(self):
        if self.postfix:
            return "N({}).{}".format(self.name, self.postfix)
        else:
            return "N(" + self.name + ")"

    def __repr__(self):
        return self.__str__()


class AssignmentNode(BinaryExpr):
    def __init__(self):
        BinaryExpr.__init__(self)


class BlockStmt(Node):
    def __init__(self):
        Node.__init__(self)

        self.lines = []

    def __str__(self):
        s = "Block{\n"
        for line in self.lines:
            s += (str(line) + ";\n")
        return s + "}"

    def __repr__(self):
        return self.__str__()


class CondStmt(Node):
    def __init__(self):
        Node.__init__(self)

        self.condition = None


class IfStmt(CondStmt):
    def __init__(self):
        CondStmt.__init__(self)

        self.then_block = None
        self.else_block = None

    def __str__(self):
        return "if({} then {} else {})".format(self.condition, self.then_block, self.else_block)

    def __repr__(self):
        return self.__str__()


class WhileStmt(CondStmt):
    def __init__(self):
        CondStmt.__init__(self)

        self.body = None

    def __str__(self):
        return "while({} do {})".format(self.condition, self.body)

    def __repr__(self):
        return self.__str__()


class StringLiteral(LeafNode):
    def __init__(self, s):
        LeafNode.__init__(self)

        self.string = s

    def __str__(self):
        return "String({})".format(self.string)


class DefStmt(Node):
    def __init__(self, f_name):
        Node.__init__(self)

        self.name = f_name
        self.params = []
        self.body = None

    def __str__(self):
        return "func({}({}) -> {})".format(self.name, self.params, self.body)

    def __repr__(self):
        return self.__str__()


class FuncCall(LeafNode):
    def __init__(self, f_name):
        LeafNode.__init__(self)

        self.f_name = f_name
        # self.filled = False
        self.args = None

    # def set_args(self, args):
    #     self.args = args
    #     self.filled = True

    def __str__(self):
        return "{}({})".format(self.f_name, self.args)

    def __repr__(self):
        return self.__str__()


class ClassStmt(Node):
    def __init__(self, name):
        Node.__init__(self)

        self.class_name = name
        self.block = None

    def __str__(self):
        return "Class {}: {}".format(self.class_name, self.block)

    def __repr__(self):
        return self.__str__()


class ClassInit(LeafNode):
    def __init__(self, name):
        LeafNode.__init__(self)

        self.class_name = name

    def __str__(self):
        return "ClassInit {}".format(self.class_name)

    def __repr__(self):
        return self.__str__()


class Postfix:
    def __init__(self):
        pass


class Dot(OperatorNode):
    def __init__(self, extra):
        OperatorNode.__init__(self, extra)

        self.operation = "."

    def __str__(self):
        return "{} dot {}".format(self.left, self.right)

    def __repr__(self):
        return self.__str__()


def parse_expr(lst):
    while len(lst) > 1:
        max_pre = 0
        index = 0
        for i in range(len(lst)):
            node = lst[i]
            if isinstance(node, OperatorNode):
                pre = node.precedence()
                # print(str(pre) + node.operation)
                if pre > max_pre and not node.left and not node.right:
                    max_pre = pre
                    index = i
        operator = lst[index]
        operator.left = lst[index - 1]
        operator.right = lst[index + 1]
        lst.pop(index + 1)
        lst.pop(index - 1)
    return lst[0]
