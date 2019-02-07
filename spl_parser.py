import spl_lexer as lex

PRECEDENCE = {"+": 50, "-": 50, "*": 100, "/": 100, "%": 100,
              "==": 20, ">": 25, "<": 25, ">=": 25, "<=": 25,
              "!=": 20, "&&": 5, "||": 5, "&": 12, "^": 11, "|": 10,
              "<<": 40, ">>": 40,
              ".": 500, "!": 200, "neg": 200, "return": 1,
              "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
              "&=": 2, "^=": 2, "|=": 2, "<<=": 2, ">>=": 2, "=>": 500}

MULTIPLIER = 1000


class Parser:
    """
    :type inner: Parser
    """

    def __init__(self):
        self.elements = []
        self.stack = []
        self.inner = None
        self.in_expr = False
        self.in_get = False
        # self.condition = None

    def __str__(self):
        return str(self.elements)

    def add_name(self, line, n):
        if self.inner:
            self.inner.add_name(line, n)
        else:
            node = NameNode(line, n)
            self.stack.append(node)

    def add_number(self, line, v):
        if self.inner:
            self.inner.add_number(line, v)
        else:
            node = get_number_node(line, v)
            self.stack.append(node)

    def add_literal(self, line, lit):
        if self.inner:
            self.inner.add_literal(line, lit)
        else:
            node = LiteralNode(line, lit)
            self.stack.append(node)

    def add_operator(self, line, op, extra_precedence, assignment=False):
        if self.inner:
            self.inner.add_operator(line, op, extra_precedence, assignment)
        else:
            self.in_expr = True
            op_node = OperatorNode(line, extra_precedence)
            op_node.assignment = assignment
            op_node.operation = op
            self.stack.append(op_node)

    def add_neg(self, line, extra_precedence):
        if self.inner:
            self.inner.add_neg(line, extra_precedence)
        else:
            self.in_expr = True
            node = NegativeExpr(line, extra_precedence)
            self.stack.append(node)

    def add_not(self, line, extra_precedence):
        if self.inner:
            self.inner.add_not(line, extra_precedence)
        else:
            self.in_expr = True
            node = NotExpr(line, extra_precedence)
            self.stack.append(node)

    def add_assignment(self, line):
        if self.inner:
            self.inner.add_assignment(line)
        else:
            # print(len(self.stack))

            name = self.stack.pop()
            ass_node = AssignmentNode(line)
            ass_node.left = name
            ass_node.operation = "="
            self.stack.append(ass_node)

    def add_if(self, line):
        if self.inner:
            self.inner.add_if(line)
        else:
            ifs = IfStmt(line)
            self.stack.append(ifs)
            self.inner = Parser()

    def add_else(self):
        if self.inner:
            self.inner.add_else()
        else:
            pass
            # node = self.stack.pop()

    def add_while(self, line):
        if self.inner:
            self.inner.add_while(line)
        else:
            whs = WhileStmt(line)
            self.stack.append(whs)
            self.inner = Parser()

    def add_for_loop(self, line):
        if self.inner:
            self.inner.add_for_loop(line)
        else:
            fls = ForLoopStmt(line)
            self.stack.append(fls)
            self.inner = Parser()

    def add_function(self, line, f_name):
        if self.inner:
            self.inner.add_function(line, f_name)
        else:
            func = DefStmt(line, f_name)
            self.stack.append(func)

    def build_func_params(self, params: list, presets: list):
        if self.inner:
            self.inner.build_func_params(params, presets)
        else:
            func = self.stack.pop()
            loc = (func.line_num, func.file)
            lst = [NameNode(loc, x) for x in params]
            pst = []
            for a in presets:
                if isinstance(a, lex.IdToken):
                    sbl = a.symbol
                    if sbl in lex.RESERVED:
                        if sbl == "true" or sbl == "false":
                            pst.append(BooleanStmt(loc, sbl))
                        elif sbl == "null":
                            pst.append(NullStmt(loc))
                        else:
                            lex.unexpected_token(a)
                    else:
                        pst.append(NameNode(loc, sbl))
                elif isinstance(a, lex.NumToken):
                    pst.append(get_number_node(loc, a.value))
                elif isinstance(a, lex.LiteralToken):
                    pst.append(LiteralNode(loc, a.text))
                elif isinstance(a, lex.InvalidToken):
                    pst.append(a)
                else:
                    lex.unexpected_token(a)
            func.params = lst
            func.presets = pst
            self.stack.append(func)

    def add_call(self, line, f_name):
        # print(f_name)
        if self.inner:
            self.inner.add_call(line, f_name)
        else:
            fc = FuncCall(line, f_name)
            self.stack.append(fc)
            self.inner = Parser()

    def add_anonymous_call(self, line, extra):
        if self.inner:
            self.inner.add_anonymous_call(line, extra)
        else:
            self.in_expr = True
            op_node = AnonymousCall(line, extra)
            op_node.assignment = False
            op_node.operation = "=>"
            self.stack.append(op_node)
            self.add_call(line, "=>")

    def is_in_get(self):
        if self.inner:
            return self.inner.is_in_get()
        else:
            return self.in_get

    def add_get_set(self, line):
        if self.inner:
            self.inner.add_get_set(line)
        else:
            self.add_call(line, "get/set")
            self.inner.in_get = True

    def build_get_set(self, is_set):
        if self.inner.inner:
            self.inner.build_get_set(is_set)
        else:
            i = len(self.stack) - 1
            if is_set:
                while i >= 0:
                    node = self.stack[i]
                    if isinstance(node, FuncCall) and node.f_name == "get/set":
                        node.f_name = "__setitem__"
                        break
                    i -= 1
            else:
                while i >= 0:
                    node = self.stack[i]
                    if isinstance(node, FuncCall) and node.f_name == "get/set":
                        node.f_name = "__getitem__"
                        break
                    i -= 1

    def add_return(self, line):
        if self.inner:
            self.inner.add_return(line)
        else:
            self.in_expr = True
            rtn = ReturnStmt(line)
            self.stack.append(rtn)

    def add_break(self, line):
        if self.inner:
            self.inner.add_break(line)
        else:
            node = BreakStmt(line)
            self.stack.append(node)

    def add_continue(self, line):
        if self.inner:
            self.inner.add_continue(line)
        else:
            node = ContinueStmt(line)
            self.stack.append(node)

    def add_bool(self, line, v):
        if self.inner:
            self.inner.add_bool(line, v)
        else:
            node = BooleanStmt(line, v)
            self.stack.append(node)

    def add_null(self, line):
        if self.inner:
            self.inner.add_null(line)
        else:
            node = NullStmt(line)
            self.stack.append(node)

    def build_call(self):
        if self.inner.inner:
            self.inner.build_call()
        # elif self.condition.condition:
        #     self.condition.build_call()
        else:
            # line = self.condition.get_as_line()
            self.inner.build_line()

            block: BlockStmt = self.inner.get_as_block()
            self.inner = None
            call = self.stack.pop()
            if len(self.stack) > 0 and isinstance(self.stack[-1], ClassInit):
                call = self.stack.pop()
            call.args = block
            self.stack.append(call)

    def build_condition(self):
        if self.inner.inner:
            self.inner.build_condition()
        else:
            self.inner.build_line()
            expr = self.inner.get_as_block()
            # print(expr)
            self.inner = None
            cond_stmt: CondStmt = self.stack.pop()
            cond_stmt.condition = expr
            # print(cond_stmt)
            self.stack.append(cond_stmt)

    def new_block(self):
        if self.inner:
            self.inner.new_block()
        else:
            self.inner = Parser()

    def add_class(self, line, class_name):
        if self.inner:
            self.inner.add_class(line, class_name)
        else:
            cs = ClassStmt(line, class_name)
            self.stack.append(cs)

    def add_extends(self, superclass_name):
        if self.inner:
            self.inner.add_extends(superclass_name)
        else:
            cs: ClassStmt = self.stack[-1]
            cs.superclass_name = superclass_name

    def build_class(self):
        if self.inner:
            self.inner.build_class()
        else:
            node = self.stack.pop()
            class_node = self.stack.pop()
            class_node.block = node
            self.stack.append(class_node)

    def add_class_new(self, line, class_name):
        if self.inner:
            self.inner.add_class_new(line, class_name)
        else:
            node = ClassInit(line, class_name)
            self.stack.append(node)

    def add_dot(self, line, extra_precedence):
        if self.inner:
            self.inner.add_dot(line, extra_precedence)
        else:
            self.in_expr = True
            node = Dot(line, extra_precedence)
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
            if not self.in_expr:
                return
            self.in_expr = False
            # print(type(self.stack[1]))
            lst = []
            while len(self.stack) > 0:
                node = self.stack[-1]
                if isinstance(node, NumNode) or isinstance(node, NameNode) or isinstance(node, OperatorNode) or \
                        isinstance(node, UnaryOperator) or isinstance(node, LiteralNode) or \
                        (isinstance(node, FuncCall) and node.args is not None) or isinstance(node, ClassInit) or \
                        isinstance(node, NullStmt) or isinstance(node, BooleanStmt):
                    lst.append(node)
                    self.stack.pop()
                else:
                    break
            lst.reverse()

            # print(lst)
            if len(lst) > 0:
                node = parse_expr(lst)
                self.stack.append(node)

    def build_line(self):
        if self.inner:
            self.inner.build_line()
        else:
            self.build_expr()
            if len(self.stack) > 0:
                res = self.stack.pop()
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
                    elif isinstance(node, WhileStmt) or isinstance(node, ForLoopStmt):
                        node.body = res
                        res = node
                    elif isinstance(node, DefStmt):
                        node.body = res
                        res = node
                    elif isinstance(node, ReturnStmt):
                        node.value = res
                        res = node
                    else:
                        res = node
                self.elements.append(res)

    def get_as_block(self):
        block = BlockStmt((0, "block"))
        block.lines = self.elements
        return block


def get_number_node(line, v: str):
    if "." in v:
        return FloatNode(line, v)
    else:
        return IntNode(line, v)


class Node:
    def __init__(self, line):
        self.line_num = line[0]
        self.file = line[1]


class LeafNode(Node):
    def __init__(self, line):
        Node.__init__(self, line)


class BinaryExpr(Node):
    """
    :type operation: str
    :type left:
    """

    def __init__(self, line):
        Node.__init__(self, line)

        self.left = None
        self.right = None
        self.operation = None

    def __str__(self):
        return "BE({} {} {})".format(self.left, self.operation, self.right)

    def __repr__(self):
        return self.__str__()


class NumNode(LeafNode):
    def __init__(self, line, v):
        LeafNode.__init__(self, line)

        self.value = v

    def __str__(self):
        return "Num(" + self.value + ")"

    def __repr__(self):
        return self.__str__()


class IntNode(NumNode):
    def __init__(self, line, v):
        NumNode.__init__(self, line, v)


class FloatNode(NumNode):
    def __init__(self, line, v):
        NumNode.__init__(self, line, v)


class LiteralNode(LeafNode):
    def __init__(self, line, lit):
        LeafNode.__init__(self, line)

        self.literal = lit

    def __str__(self):
        return '"' + self.literal + '"'

    def __repr__(self):
        return self.__str__()


class OperatorNode(BinaryExpr):
    def __init__(self, line, extra):
        BinaryExpr.__init__(self, line)

        self.assignment = False
        self.extra_precedence = extra * MULTIPLIER
        # print(self.extra_precedence)

    def precedence(self):
        return PRECEDENCE[self.operation] + self.extra_precedence


class UnaryOperator(Node):

    def __init__(self, line, extra):
        Node.__init__(self, line)

        self.value = None
        self.operation = None
        self.extra_precedence = extra * MULTIPLIER

    def precedence(self):
        return PRECEDENCE[self.operation] + self.extra_precedence

    def __str__(self):
        return "UE({} {})".format(self.operation, self.value)

    def __repr__(self):
        return self.__str__()


class NameNode(LeafNode):
    def __init__(self, line, n):
        LeafNode.__init__(self, line)

        self.name = n
        self.index = None
        # self.nest = None

    def __str__(self):
        return "N(" + self.name + ")"

    def __repr__(self):
        return self.__str__()


class AssignmentNode(BinaryExpr):
    def __init__(self, line):
        BinaryExpr.__init__(self, line)


class AnonymousCall(OperatorNode):
    def __init__(self, line, extra):
        OperatorNode.__init__(self, line, extra)


class NegativeExpr(UnaryOperator):
    def __init__(self, line, extra):
        UnaryOperator.__init__(self, line, extra)

        self.operation = "neg"


class NotExpr(UnaryOperator):
    def __init__(self, line, extra):
        UnaryOperator.__init__(self, line, extra)

        self.operation = "!"


class ReturnStmt(UnaryOperator):
    def __init__(self, line):
        UnaryOperator.__init__(self, line, 0)

        self.operation = "return"


class BreakStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

    def __str__(self):
        return "break"

    def __repr__(self):
        return self.__str__()


class ContinueStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

    def __str__(self):
        return "continue"

    def __repr__(self):
        return self.__str__()


class BooleanStmt(LeafNode):
    def __init__(self, line, v):
        LeafNode.__init__(self, line)

        self.value = v

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


class NullStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

    def __str__(self):
        return "null"

    def __repr__(self):
        return self.__str__()


class BlockStmt(Node):
    def __init__(self, line):
        Node.__init__(self, line)

        self.lines = []

    def __str__(self):
        s = "Block{\n"
        for line in self.lines:
            s += (str(line) + ";\n")
        return s + "}"

    def __repr__(self):
        return self.__str__()


class CondStmt(Node):
    def __init__(self, line):
        Node.__init__(self, line)

        self.condition = None


class IfStmt(CondStmt):
    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.then_block = None
        self.else_block = None

    def __str__(self):
        return "if({} then {} else {})".format(self.condition, self.then_block, self.else_block)

    def __repr__(self):
        return self.__str__()


class WhileStmt(CondStmt):
    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.body = None

    def __str__(self):
        return "while({} do {})".format(self.condition, self.body)

    def __repr__(self):
        return self.__str__()


class ForLoopStmt(CondStmt):
    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.body = None
        # self.stop = self.condition

    def __str__(self):
        return "for ({}) do {}".format(self.condition, self.body)

    def __repr__(self):
        return self.__str__()


class DefStmt(Node):
    def __init__(self, line, f_name):
        Node.__init__(self, line)

        self.name = f_name
        self.params = []
        self.presets = []
        self.body = None

    def __str__(self):
        return "func({}({} :{}) -> {})".format(self.name, self.params, self.presets, self.body)

    def __repr__(self):
        return self.__str__()


class FuncCall(LeafNode):
    """
    :type args: BlockStmt
    """
    def __init__(self, line, f_name):
        LeafNode.__init__(self, line)

        self.f_name = f_name
        self.args = None
        self.is_get_set = False
        # self.header_block = None

    def __str__(self):
        return "{}({})".format(self.f_name, self.args)

    def __repr__(self):
        return self.__str__()


class ClassStmt(Node):
    def __init__(self, line, name):
        Node.__init__(self, line)

        self.class_name = name
        self.superclass_name = None
        self.block = None

    def __str__(self):
        return "Class {}: {}".format(self.class_name, self.block)

    def __repr__(self):
        return self.__str__()


class ClassInit(LeafNode):
    def __init__(self, line, name):
        LeafNode.__init__(self, line)

        self.class_name = name
        self.args = None

    def __str__(self):
        if self.args:
            return "ClassInit {}({})".format(self.class_name, self.args)
        else:
            return "ClassInit {}".format(self.class_name)

    def __repr__(self):
        return self.__str__()


class Dot(OperatorNode):
    def __init__(self, line, extra):
        OperatorNode.__init__(self, line, extra)

        self.operation = "."

    def __str__(self):
        return "({} dot {})".format(self.left, self.right)

    def __repr__(self):
        return self.__str__()


# class ContinueCall(OperatorNode):
#     def __init__(self, extra):
#         OperatorNode.__init__(self, extra)
#
#         self.operation = ")("
#
#     def __str__(self):
#         return "{}>>{}".format(self.left, self.right)
#
#     def __repr__(self):
#         return self.__str__()


def parse_expr(lst):
    # print(lst)
    while len(lst) > 1:
        max_pre = 0
        index = 0
        for i in range(len(lst)):
            node = lst[i]
            if isinstance(node, UnaryOperator):
                pre = node.precedence()
                if pre > max_pre and not node.value:
                    max_pre = pre
                    index = i
            elif isinstance(node, OperatorNode):
                pre = node.precedence()
                if pre > max_pre and not node.left and not node.right:
                    max_pre = pre
                    index = i
        operator = lst[index]
        if isinstance(operator, UnaryOperator):
            operator.value = lst[index + 1]
            lst.pop(index + 1)
        else:
            operator.left = lst[index - 1]
            operator.right = lst[index + 1]
            lst.pop(index + 1)
            lst.pop(index - 1)
    return lst[0]
