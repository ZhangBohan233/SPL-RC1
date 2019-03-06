PRECEDENCE = {"+": 50, "-": 50, "*": 100, "/": 100, "%": 100,
              "==": 20, ">": 25, "<": 25, ">=": 25, "<=": 25,
              "!=": 20, "&&": 5, "||": 5, "&": 12, "^": 11, "|": 10,
              "<<": 40, ">>": 40, "unpack": 200,
              ".": 500, "!": 200, "neg": 200, "return": 1, "throw": 1,
              "+=": 2, "-=": 2, "*=": 2, "/=": 2, "%=": 2,
              "&=": 2, "^=": 2, "|=": 2, "<<=": 2, ">>=": 2, "=>": 500,
              "===": 20, "!==": 20, "instanceof": 25}

MULTIPLIER = 1000

# NODE = 0
INT_NODE = 1
FLOAT_NODE = 2
LITERAL_NODE = 3
NAME_NODE = 4
BOOLEAN_STMT = 5
NULL_STMT = 6
BREAK_STMT = 7
CONTINUE_STMT = 8
ASSIGNMENT_NODE = 9
DOT = 10
ANONYMOUS_CALL = 11
OPERATOR_NODE = 12
NEGATIVE_EXPR = 13
NOT_EXPR = 14
RETURN_STMT = 15
BLOCK_STMT = 16
IF_STMT = 17
WHILE_STMT = 18
FOR_LOOP_STMT = 19
DEF_STMT = 20
FUNCTION_CALL = 21
CLASS_STMT = 22
CLASS_INIT = 23
# INVALID_TOKEN = 24
ABSTRACT = 25
THROW_STMT = 26
TRY_STMT = 27
CATCH_STMT = 28
TYPE_NODE = 29
# UNPACK_OPERATOR = 30
JUMP_NODE = 30
UNDEFINED_NODE = 31

ASSIGN = 0
CONST = 1
VAR = 2


class AbstractSyntaxTree:
    """
    :type inner: AbstractSyntaxTree
    """

    def __init__(self):
        self.elements: BlockStmt = BlockStmt((0, "parser"))
        self.stack = []
        self.inner = None
        self.in_expr = False
        self.in_get = False

    def __str__(self):
        return str(self.elements)

    def get_active(self):
        if self.inner:
            return self.inner.get_active()
        else:
            return self

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

    # def add_unpack(self, line, extra_precedence):
    #     if self.inner:
    #         self.inner.add_unpack(line, extra_precedence)
    #     else:
    #         self.in_expr = True
    #         node = UnpackOperator(line, extra_precedence)
    #         self.stack.append(node)

    def add_assignment(self, line, var_level):
        if self.inner:
            self.inner.add_assignment(line, var_level)
        else:
            # print(len(self.stack))

            name = self.stack.pop()
            ass_node = AssignmentNode(line, var_level)
            ass_node.left = name
            self.stack.append(ass_node)

    def add_undefined(self, line):
        if self.inner:
            self.inner.add_undefined(line)
        else:
            node = UndefinedNode(line)
            self.stack.append(node)

    def add_type(self, line):
        if self.inner:
            self.inner.add_type(line)
        else:
            name = self.stack.pop()
            tp_node = TypeNode(line)
            tp_node.left = name
            self.stack.append(tp_node)

    def add_if(self, line):
        if self.inner:
            self.inner.add_if(line)
        else:
            ifs = IfStmt(line)
            self.stack.append(ifs)
            self.inner = AbstractSyntaxTree()

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
            self.inner = AbstractSyntaxTree()

    def add_for_loop(self, line):
        if self.inner:
            self.inner.add_for_loop(line)
        else:
            fls = ForLoopStmt(line)
            self.stack.append(fls)
            self.inner = AbstractSyntaxTree()

    def add_throw(self, line):
        if self.inner:
            self.inner.add_throw(line)
        else:
            self.in_expr = True
            thr = ThrowStmt(line)
            self.stack.append(thr)

    def add_try(self, line):
        if self.inner:
            self.inner.add_try(line)
        else:
            tb = TryStmt(line)
            self.stack.append(tb)
            # self.inner = AbstractSyntaxTree()

    def add_catch(self, line):
        if self.inner:
            self.inner.add_catch(line)
        else:
            cat = CatchStmt(line)
            self.stack.append(cat)
            self.inner = AbstractSyntaxTree()

    def add_finally(self, line):
        if self.inner:
            self.inner.add_finally(line)
        else:
            pass
            # self.inner = AbstractSyntaxTree()

    def add_function(self, line, f_name, abstract: bool, tags: list):
        if self.inner:
            self.inner.add_function(line, f_name, abstract, tags)
        else:
            func = DefStmt(line, f_name, abstract, tags)
            self.stack.append(func)
            self.inner = AbstractSyntaxTree()

    def build_func_params(self):
        if self.inner.inner:
            self.inner.build_func_params()
        else:
            self.inner.build_line()
            block = self.inner.get_as_block()
            self.inner = None
            function = self.stack.pop()
            function.params = block
            self.stack.append(function)

    def add_call(self, line, f_name):
        # print(f_name)
        if self.inner:
            self.inner.add_call(line, f_name)
        else:
            fc = FuncCall(line, f_name)
            self.stack.append(fc)
            self.inner = AbstractSyntaxTree()

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
            self.inner = AbstractSyntaxTree()

    def add_class(self, line, class_name, abstract: bool):
        if self.inner:
            self.inner.add_class(line, class_name, abstract)
        else:
            cs = ClassStmt(line, class_name, abstract)
            self.stack.append(cs)

    def get_current_class(self):
        if self.inner:
            return self.inner.get_current_class()
        else:
            return self.stack[-1]

    def add_extends(self, superclass_name: str, target_class):
        if self.inner:
            self.inner.add_extends(superclass_name, target_class)
        else:
            # cs: ClassStmt = self.stack[-1]
            # cs.superclass_name = superclass_name
            target_class: ClassStmt
            target_class.superclass_names.append(superclass_name)

    # def add_abstract(self, line):
    #     if self.inner:
    #         self.inner.add_abstract(line)
    #     else:
    #         self.stack.append(Abstract(line))

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
            # print(self.stack)
            self.build_expr()
            if len(self.stack) > 0:
                lst = [self.stack.pop()]
                while len(self.stack) > 0:
                    node = self.stack.pop()
                    if isinstance(node, LeafNode):
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                        # res = node
                    elif isinstance(node, BinaryExpr) and len(lst) > 0:
                        node.right = lst[0]
                        lst[0] = node
                    elif isinstance(node, BlockStmt):
                        if len(lst) > 0:
                            lst.insert(0, node)
                        else:
                            lst.append(node)
                            # res = node
                    elif isinstance(node, IfStmt):
                        node.then_block = lst[0]
                        if len(lst) > 1:
                            node.else_block = lst[1]
                        lst.clear()
                        lst.append(node)
                    elif isinstance(node, WhileStmt) or isinstance(node, ForLoopStmt):
                        node.body = lst[0] if len(lst) > 0 else None
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, DefStmt):
                        node.body = lst[0] if len(lst) > 0 else None
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, ReturnStmt) or isinstance(node, ThrowStmt):
                        node.value = lst[0] if len(lst) > 0 else None
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, CatchStmt):
                        node.then = lst[0] if len(lst) > 0 else None
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                    elif isinstance(node, TryStmt):
                        node.try_block = lst[0]
                        if isinstance(lst[-1], CatchStmt):
                            node.catch_blocks = lst[1:]
                        else:
                            node.catch_blocks = lst[1:-1]
                            node.finally_block = lst[-1]
                        lst.clear()
                        lst.append(node)
                    else:
                        lst.__setitem__(0, node) if len(lst) > 0 else lst.append(node)
                        # res = node
                self.elements.add_line(lst[0])

    def get_as_block(self):
        return self.elements


def get_number_node(line, v: str):
    if "." in v:
        return FloatNode(line, v)
    else:
        return IntNode(line, v)


class Node:
    line_num = 0
    file = None
    node_type = 0
    execution = 0

    def __init__(self, line: tuple):
        self.line_num = line[0]
        self.file = line[1]
        self.node_type = 0
        self.execution = 0


class LeafNode(Node):
    def __init__(self, line):
        Node.__init__(self, line)


class BinaryExpr(Node):
    """
    :type operation: str
    :type left:
    """
    left = None
    right = None
    operation = None

    def __init__(self, line):
        Node.__init__(self, line)

        # self.left = None
        # self.right = None
        # self.operation = None

    def __str__(self):
        return "BE({} {} {})".format(self.left, self.operation, self.right)

    def __repr__(self):
        return self.__str__()


class NumNode(LeafNode):
    value = 0

    def __init__(self, line, v):
        LeafNode.__init__(self, line)

        self.value = v

    def __str__(self):
        return "Num(" + str(self.value) + ")"

    def __repr__(self):
        return self.__str__()


class IntNode(NumNode):
    def __init__(self, line, v):
        NumNode.__init__(self, line, int(v))

        self.node_type = INT_NODE


class FloatNode(NumNode):
    def __init__(self, line, v):
        NumNode.__init__(self, line, float(v))

        self.node_type = FLOAT_NODE


class LiteralNode(LeafNode):
    """
    :type literal: str
    """
    literal = None

    def __init__(self, line, lit):
        LeafNode.__init__(self, line)

        self.node_type = LITERAL_NODE
        self.literal = lit

    def __str__(self):
        return '"' + self.literal + '"'

    def __repr__(self):
        return self.__str__()


class TitleNode(Node):
    titles: list

    def __init__(self, line):
        Node.__init__(self, line)


class OperatorNode(BinaryExpr):
    assignment = False
    extra_precedence = 0

    def __init__(self, line, extra):
        BinaryExpr.__init__(self, line)

        self.node_type = OPERATOR_NODE
        # self.assignment = False
        self.extra_precedence = extra * MULTIPLIER
        # print(self.extra_precedence)

    def precedence(self):
        return PRECEDENCE[self.operation] + self.extra_precedence


class UnaryOperator(Node):
    value = None
    operation = None
    extra_precedence = 0

    def __init__(self, line, extra):
        Node.__init__(self, line)

        # self.value = None
        # self.operation = None
        self.extra_precedence = extra * MULTIPLIER

    def precedence(self):
        return PRECEDENCE[self.operation] + self.extra_precedence

    def __str__(self):
        return "UE({} {})".format(self.operation, self.value)

    def __repr__(self):
        return self.__str__()


class NameNode(LeafNode):
    name = None

    def __init__(self, line, n):
        LeafNode.__init__(self, line)

        self.node_type = NAME_NODE
        self.name = n

    def __str__(self):
        # if self.auth == stl.PUBLIC:
        return "N(" + self.name + ")"
        # else:
        #     return "N(private " + self.name + ")"

    def __repr__(self):
        return self.__str__()


class AssignmentNode(BinaryExpr):
    level = ASSIGN

    def __init__(self, line, level):
        BinaryExpr.__init__(self, line)

        self.node_type = ASSIGNMENT_NODE
        self.operation = "="
        self.level = level


class TypeNode(BinaryExpr):
    def __init__(self, line):
        BinaryExpr.__init__(self, line)

        self.node_type = TYPE_NODE
        self.operation = ":"


class AnonymousCall(OperatorNode):
    def __init__(self, line, extra):
        OperatorNode.__init__(self, line, extra)

        self.node_type = ANONYMOUS_CALL


class NegativeExpr(UnaryOperator):
    def __init__(self, line, extra):
        UnaryOperator.__init__(self, line, extra)

        self.node_type = NEGATIVE_EXPR
        self.operation = "neg"


class NotExpr(UnaryOperator):
    def __init__(self, line, extra):
        UnaryOperator.__init__(self, line, extra)

        self.node_type = NOT_EXPR
        self.operation = "!"


# class UnpackOperator(LeafNode):
#     def __init__(self, line):
#         LeafNode.__init__(self, line)
#
#         node_type = UNPACK_OPERATOR


class ReturnStmt(UnaryOperator):
    def __init__(self, line):
        UnaryOperator.__init__(self, line, 0)

        self.node_type = RETURN_STMT
        self.operation = "return"


class BreakStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = BREAK_STMT

    def __str__(self):
        return "break"

    def __repr__(self):
        return self.__str__()


class ContinueStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = CONTINUE_STMT

    def __str__(self):
        return "continue"

    def __repr__(self):
        return self.__str__()


class BooleanStmt(LeafNode):
    value = None

    def __init__(self, line, v):
        LeafNode.__init__(self, line)

        self.node_type = BOOLEAN_STMT
        self.value = v

    def __str__(self):
        return "Bool:" + self.value

    def __repr__(self):
        return self.__str__()


class NullStmt(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = NULL_STMT

    def __str__(self):
        return "null"

    def __repr__(self):
        return self.__str__()


class BlockStmt(Node):
    lines: list = None

    def __init__(self, line):
        Node.__init__(self, line)

        self.node_type = BLOCK_STMT

        self.lines = []

    def add_line(self, node: Node):
        self.lines.append(node)

    def __str__(self):
        s = "Block{\n"
        for line in self.lines:
            s += (str(line) + ";\n")
        if self.execution == 0:
            return s + "}"
        else:
            return s + "}: " + str(self.execution)

    def __repr__(self):
        return self.__str__()


class CondStmt(Node):
    condition = None

    def __init__(self, line):
        Node.__init__(self, line)

        # self.condition = None


class IfStmt(CondStmt):
    then_block = None
    else_block = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = IF_STMT
        # self.then_block = None
        # self.else_block = None

    def __str__(self):
        return "if({} then {} else {})".format(self.condition, self.then_block, self.else_block)

    def __repr__(self):
        return self.__str__()


class WhileStmt(CondStmt):
    body = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = WHILE_STMT
        # self.body = None

    def __str__(self):
        return "while({} do {})".format(self.condition, self.body)

    def __repr__(self):
        return self.__str__()


class ForLoopStmt(CondStmt):
    body = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = FOR_LOOP_STMT
        # self.body = None

    def __str__(self):
        return "for ({}) do {}".format(self.condition, self.body)

    def __repr__(self):
        return self.__str__()


class DefStmt(TitleNode):
    name = None
    params: BlockStmt = None
    body = None
    abstract: bool = False
    tags: list

    def __init__(self, line, f_name, abstract: bool, tags: list):
        TitleNode.__init__(self, line)
        # Limited.__init__(self, auth)

        self.node_type = DEF_STMT
        self.name = f_name
        self.params = None
        self.abstract = abstract
        self.tags = tags

    def __str__(self):
        return "func({}({}) -> {})".format(self.name, self.params, self.body)

    def __repr__(self):
        return self.__str__()


class FuncCall(LeafNode):
    """
    :type args: BlockStmt
    """
    f_name = None
    args = None
    is_get_set = False

    def __init__(self, line, f_name):
        LeafNode.__init__(self, line)

        self.node_type = FUNCTION_CALL
        self.f_name = f_name
        # self.args = None
        # self.is_get_set = False

    def __str__(self):
        return "{}({})".format(self.f_name, self.args)

    def __repr__(self):
        return self.__str__()


class ClassStmt(Node):
    class_name: str = None
    superclass_names: list = None
    block: BlockStmt = None
    abstract: bool = False

    def __init__(self, line: tuple, name: str, abstract: bool):
        Node.__init__(self, line)

        self.node_type = CLASS_STMT
        self.class_name = name
        self.abstract = abstract
        self.superclass_names = []
        # self.block = None

    def __str__(self):
        return "Class {}: {}".format(self.class_name, self.block)

    def __repr__(self):
        return self.__str__()


class ClassInit(LeafNode):
    class_name = None
    args: BlockStmt = None

    def __init__(self, line, name):
        LeafNode.__init__(self, line)

        self.node_type = CLASS_INIT
        self.class_name = name
        # self.args: BlockStmt = None

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

        self.node_type = DOT
        self.operation = "."

    def __str__(self):
        return "({} dot {})".format(self.left, self.right)

    def __repr__(self):
        return self.__str__()


class ThrowStmt(UnaryOperator):
    def __init__(self, line):
        UnaryOperator.__init__(self, line, 0)

        self.node_type = THROW_STMT
        self.operation = "throw"

    def __str__(self):
        return "Throw({})".format(self.value)

    def __repr__(self):
        return self.__str__()


class CatchStmt(CondStmt):
    then: BlockStmt = None

    def __init__(self, line):
        CondStmt.__init__(self, line)

        self.node_type = CATCH_STMT
        # self.then: BlockStmt = None

    def __str__(self):
        return "catch ({}) {}".format(self.condition, self.then)

    def __repr__(self):
        return self.__str__()


class TryStmt(Node):
    try_block: BlockStmt = None
    catch_blocks = None
    finally_block: BlockStmt = None

    def __init__(self, line):
        Node.__init__(self, line)

        self.node_type = TRY_STMT
        # self.try_block: BlockStmt = None
        self.catch_blocks: [CatchStmt] = []
        # self.finally_block: BlockStmt = None

    def __str__(self):
        return "try {} {} finally {}" \
            .format(self.try_block, self.catch_blocks, self.finally_block)

    def __repr__(self):
        return self.__str__()


class JumpNode(Node):
    to = None
    args = None

    def __init__(self, line, to):
        Node.__init__(self, line)

        self.node_type = JUMP_NODE
        self.to = to
        self.args = []

    def __str__(self):
        return "Jump({}: {})".format(self.to, self.args)

    def __repr__(self):
        return self.__str__()


class UndefinedNode(LeafNode):
    def __init__(self, line):
        LeafNode.__init__(self, line)

        self.node_type = UNDEFINED_NODE

    def __str__(self):
        return "undefined"

    def __repr__(self):
        return self.__str__()


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