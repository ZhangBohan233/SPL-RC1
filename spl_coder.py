from spl_parser import *
import struct


# FLAGS


class Coder:
    def __init__(self):
        self.lst = []

    def add_int(self, value: int, length):
        b = value.to_bytes(length, "big", signed=True)
        self.lst.extend(b)

    def add_float(self, value: float, length):
        b = bytes(struct.pack("d", value))
        print(12312)
        for x in b:
            self.lst.append(x)

    def add_literal(self, value: str):
        ba = value.encode(encoding="utf8")
        length = len(ba)
        self.add_int(length, 4)  # record the length of string
        self.lst.extend(ba)

    def codes(self, node: Node):
        if node is None:
            self.add_int(-1, 1)
        else:
            t = node.type
            self.add_int(t, 1)  # Record the type flag
            self.add_int(node.line_num, 4)  # Record the line number
            self.add_literal(node.file)  # File name
            if t == INT_NODE:
                node: IntNode
                self.add_int(node.value, 8)
            elif t == FloatNode:
                node: FloatNode
                self.add_float(node.value, 8)
            elif t == LITERAL_NODE:
                node: LiteralNode
                self.add_literal(node.literal)
            elif t == NAME_NODE:
                node: NameNode
                self.add_int(node.auth, 1)
                self.add_literal(node.name)
            elif t == BOOLEAN_STMT:
                node: BooleanStmt
                bv = 1 if node.value == "true" else 0
                self.add_int(bv, 1)
            elif t == NULL_STMT or t == BREAK_STMT or t == CONTINUE_STMT:
                pass  # Nothing to do
            elif t == ASSIGNMENT_NODE:
                node: AssignmentNode
                ln: Node = node.left
                if ln.type == NAME_NODE:
                    ln: NameNode
                    self.add_int(0, 1)
                    self.add_literal(ln.name)
                elif node.type == DOT:
                    pass
                self.codes(node.right)
            elif t == DOT:
                node: Dot
                # self.add_int(node.extra_precedence // MULTIPLIER, 1)
                self.codes(node.left)
                self.codes(node.right)
            elif t == ANONYMOUS_CALL:
                node: AnonymousCall
                # self.add_int(node.extra_precedence // MULTIPLIER, 1)
                self.codes(node.left)
                self.codes(node.right)
            elif t == OPERATOR_NODE:
                node: OperatorNode
                # self.add_int(node.extra_precedence // MULTIPLIER, 1)
                self.add_literal(node.operation)
                self.codes(node.left)
                self.codes(node.right)
            elif t == NEGATIVE_EXPR or t == NOT_EXPR:
                node: UnaryOperator
                # self.add_int(node.extra_precedence // MULTIPLIER, 1)
                self.add_literal(node.operation)
                self.codes(node.value)
            elif t == RETURN_STMT:
                node: ReturnStmt
                self.codes(node.value)
            elif t == BLOCK_STMT:
                node: BlockStmt
                self.add_int(len(node.lines), 4)
                for line in node.lines:
                    self.codes(line)
            elif t == IF_STMT:
                node: IfStmt
                self.codes(node.condition)
                self.codes(node.then_block)
                self.codes(node.else_block)
            elif t == WHILE_STMT:
                node: WhileStmt
                self.codes(node.condition)
                self.codes(node.body)
            elif t == FOR_LOOP_STMT:
                node: ForLoopStmt
                self.codes(node.condition)
                self.codes(node.body)
            elif t == DEF_STMT:
                node: DefStmt
                self.add_int(node.auth, 1)
                self.add_literal(node.name)
                self.add_int(len(node.params), 4)  # presets have the same length as params
                for p in node.params:
                    p: NameNode
                    self.add_literal(p.name)
                for p in node.presets:
                    self.codes(p)
                self.codes(node.body)
            elif t == FUNCTION_CALL:
                node: FuncCall
                if node.is_get_set:
                    self.add_int(1, 1)
                else:
                    self.add_int(0, 1)
                self.add_literal(node.f_name)
                self.codes(node.args)
            elif t == CLASS_STMT:
                node: ClassStmt
                self.add_literal(node.class_name)
                self.add_int(len(node.superclass_names), 4)
                for sc in node.superclass_names:
                    self.add_literal(sc)
                self.codes(node.block)
            elif t == CLASS_INIT:
                node: ClassInit
                self.add_literal(node.class_name)
                self.codes(node.args)
            elif t == INVALID_TOKEN or t == ABSTRACT:
                pass
            elif t == THROW_STMT:
                pass
            elif t == TRY_STMT:
                pass
            elif t == CATCH_STMT:
                pass
            elif t == TYPE_NODE:
                node: TypeNode
                self.codes(node.left)
                self.codes(node.right)
            else:
                raise CompileException("Invalid syntax tree")

    def make_code(self, ast: BlockStmt):
        """
        Codes an spl abstract syntax tree into binary codes.
    
        :param ast:
        :return:
        """
        self.codes(ast)
        return bytes(self.lst)


class CompileException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
