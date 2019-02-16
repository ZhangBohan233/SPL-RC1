from spl_parser import *
from spl_lib import *


class Optimizer:
    def __init__(self, ast: BlockStmt):
        self.ast = ast
        self.level = 0
        self.last_func = None
        self.returning = False

    def optimize(self, level):
        self.level = level
        if level == 1 or level == 2:
            self.optimize_leaf()

    def optimize_leaf(self):
        self.ast = self.reduce_leaf(self.ast)

    def reduce_leaf(self, node: Node):
        if node is None:
            return None
        t = node.type
        if t == BLOCK_STMT:
            node: BlockStmt
            for i in range(len(node.lines)):
                node.lines[i] = self.reduce_leaf(node.lines[i])
            return node
        elif isinstance(node, NumNode):
            return node.value
        elif isinstance(node, NullStmt):
            return NULL
        elif isinstance(node, BooleanStmt):
            return TRUE if node.value == "true" else FALSE
        elif isinstance(node, LiteralNode):
            return String(node.literal)
        elif isinstance(node, BinaryExpr):
            # this reverse is done intentionally
            node.right = self.reduce_leaf(node.right)
            node.left = self.reduce_leaf(node.left)
            return node
        elif t == IF_STMT:
            node: IfStmt
            node.condition = self.reduce_leaf(node.condition)
            node.then_block = self.reduce_leaf(node.then_block)
            node.else_block = self.reduce_leaf(node.else_block)
            return node
        elif t == WHILE_STMT:
            node: WhileStmt
            node.condition = self.reduce_leaf(node.condition)
            node.body = self.reduce_leaf(node.body)
            return node
        elif t == FOR_LOOP_STMT:
            node: ForLoopStmt
            node.condition = self.reduce_leaf(node.condition)
            node.body = self.reduce_leaf(node.body)
            return node
        elif isinstance(node, UnaryOperator):
            if t == RETURN_STMT:
                node: ReturnStmt
                # v = node.value
                if self.level > 1:
                    self.returning = True
                node.value = self.reduce_leaf(node.value)
                self.returning = False
                # if isinstance(v, FuncCall):
                #     if self.last_func:
                #         if self.last_func.name == v.f_name:
                #             jn = JumpNode((node.line_num, node.file), self.last_func.name)
                #             jn.args = v.args
                #             print(jn.args)
                #             return jn
                return node
            else:
                node.value = self.reduce_leaf(node.value)
                return node
        elif t == DEF_STMT:
            node: DefStmt
            self.last_func = node
            node.body = self.reduce_leaf(node.body)
            return node
        elif t == CLASS_STMT:
            node: ClassStmt
            node.block = self.reduce_leaf(node.block)
            return node
        elif t == FUNCTION_CALL:
            node: FuncCall
            if self.returning:
                if self.last_func:
                    if self.last_func.name == node.f_name:
                        jn = JumpNode((node.line_num, node.file), self.last_func.name)
                        jn.args = node.args
                        self.returning = False
                        return jn
            return node
        else:
            return node
