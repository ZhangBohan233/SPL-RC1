import spl_ast as psr


class Optimizer:
    def __init__(self, ast: psr.BlockStmt):
        self.ast = ast
        self.level = 0
        self.last_func = None
        self.returning = False
        self.interrupt = False

    def optimize(self, level):
        self.level = level
        if level > 0:
            self.optimize_leaf()

    def optimize_leaf(self):
        self.ast = self.reduce_leaf(self.ast)

    def reduce_leaf(self, node: psr.Node):
        if node is None:
            return None
        t = node.node_type
        if t == psr.BLOCK_STMT:
            node: psr.BlockStmt
            for i in range(len(node.lines)):
                node.lines[i] = self.reduce_leaf(node.lines[i])
            return node
        elif isinstance(node, psr.NumNode):
            return node.value
        elif isinstance(node, psr.NullStmt):
            return None
        elif isinstance(node, psr.BooleanStmt):
            return node.value == "true"
        elif isinstance(node, psr.BinaryExpr):
            # this reversal is done intentionally
            node: psr.BinaryExpr
            if node.node_type == psr.DOT:
                if self.returning:
                    self.interrupt = True
            node.right = self.reduce_leaf(node.right)
            node.left = self.reduce_leaf(node.left)
            return node
        elif t == psr.IF_STMT:
            node: psr.IfStmt
            node.condition = self.reduce_leaf(node.condition)
            node.then_block = self.reduce_leaf(node.then_block)
            node.else_block = self.reduce_leaf(node.else_block)
            return node
        elif t == psr.WHILE_STMT:
            node: psr.WhileStmt
            node.condition = self.reduce_leaf(node.condition)
            node.body = self.reduce_leaf(node.body)
            return node
        elif t == psr.FOR_LOOP_STMT:
            node: psr.ForLoopStmt
            node.condition = self.reduce_leaf(node.condition)
            node.body = self.reduce_leaf(node.body)
            return node
        elif isinstance(node, psr.UnaryOperator):
            if node.value == "return":
                # v = node.value
                if self.level > 1:
                    self.returning = True
                    self.interrupt = False
                node.value = self.reduce_leaf(node.value)
                self.returning = False
                return node
            else:
                node.value = self.reduce_leaf(node.value)
                return node
        elif t == psr.DEF_STMT:
            node: psr.DefStmt
            self.last_func = node
            node.body = self.reduce_leaf(node.body)
            return node
        elif t == psr.CLASS_STMT:
            node: psr.ClassStmt
            node.block = self.reduce_leaf(node.block)
            return node
        elif t == psr.FUNCTION_CALL:
            node: psr.FuncCall
            if self.returning and not self.interrupt:
                if self.last_func:
                    if self.last_func.name == node.f_name:
                        jn = psr.JumpNode((node.line_num, node.file), self.last_func.name)
                        jn.args = node.args
                        self.returning = False
                        return jn
            return node
        else:
            return node
