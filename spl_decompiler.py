import spl_parser as psr


NO_SPACE = {".", "=>"}


class Decompiler:
    ast: psr.BlockStmt

    def __init__(self, ast):
        self.ast = ast
        self.lst = []
        self.indentation = 0
        self.new_line = True
        self.precedence = 0
        self.call_layer = 0

    def decompile(self) -> str:
        self.lst.clear()
        self.decompile_node(self.ast)
        return "".join(self.lst)

    def calculate_parenthesis(self, node):
        difference = (node.extra_precedence - self.precedence) // 1000
        self.precedence = node.extra_precedence
        front = "(" * difference
        back = ")" * difference
        return front, back

    def decompile_node(self, node):
        if isinstance(node, psr.Node):
            t = node.node_type
            if t == psr.BLOCK_STMT:
                node: psr.BlockStmt
                looped = False
                for line in node.lines:
                    if self.new_line:
                        self.lst.append(" " * self.indentation)
                    self.decompile_node(line)
                    if self.new_line:
                        self.lst.append(";\n")
                    else:
                        self.lst.append(", ")
                        looped = True
                if looped:
                    self.lst.pop()
            elif t == psr.INT_NODE:
                node: psr.IntNode
                self.lst.append(str(node.value))
            elif t == psr.FLOAT_NODE:
                node: psr.FloatNode
                self.lst.append(str(node.value))
            elif t == psr.LITERAL_NODE:
                node: psr.LiteralNode
                self.lst.append('"' + node.literal + '"')
            elif t == psr.NULL_STMT:
                self.lst.append("null")
            elif t == psr.NAME_NODE:
                node: psr.NameNode
                if node.auth == psr.stl.PRIVATE:
                    self.lst.append("private ")
                self.lst.append(node.name)
            elif t == psr.ASSIGNMENT_NODE:
                node: psr.AssignmentNode
                if node.level == psr.CONST:
                    self.lst.append("const ")
                elif node.level == psr.VAR:
                    self.lst.append("var ")
                elif node.level == psr.LOCAL:
                    self.lst.append("let ")
                self.decompile_node(node.left)
                self.lst.append(" = ")
                self.decompile_node(node.right)
            elif t == psr.IF_STMT:
                node: psr.IfStmt
                self.lst.append("if (")
                self.new_line = False
                self.decompile_node(node.condition)
                self.lst.append(") {\n")
                self.new_line = True
                self.indentation += 4
                self.decompile_node(node.then_block)
                self.indentation -= 4
                self.lst.append(" " * self.indentation + "}")
                if node.else_block:
                    self.lst.append(" else {\n")
                    self.indentation += 4
                    self.decompile_node(node.else_block)
                    self.indentation -= 4
                    self.lst.append(" " * self.indentation + "}")
            elif t == psr.WHILE_STMT or t == psr.FOR_LOOP_STMT:
                node: psr.WhileStmt
                self.lst.append("while (")
                self.new_line = False
                self.decompile_node(node.condition)
                self.lst.append(") {\n")
                self.indentation += 4
                self.new_line = True
                self.decompile_node(node.body)
                self.indentation -= 4
                self.lst.append(" " * self.indentation + "}")
            elif isinstance(node, psr.BinaryExpr):
                node: psr.OperatorNode
                # self.new_line = False
                t = self.calculate_parenthesis(node)
                front = t[0]
                back = t[1]
                self.lst.append(front)
                self.decompile_node(node.left)
                if node.operation in NO_SPACE:
                    rep = ""
                else:
                    rep = " "
                self.lst.append(rep)
                self.lst.append(str(node.operation))
                self.lst.append(rep)
                self.decompile_node(node.right)
                self.lst.append(back)
            elif t == psr.DEF_STMT:
                node: psr.DefStmt
                if node.auth == psr.stl.PRIVATE:
                    self.lst.append("private ")
                self.lst.append("function ")
                if len(node.name) < 3 or node.name[:3] != "af-":
                    self.lst.append(node.name)
                self.lst.append("(")
                for i in range(len(node.params)):
                    param = node.params[i].name
                    preset = node.presets[i]
                    if isinstance(preset, psr.InvalidToken):
                        self.lst.append(param)
                        self.lst.append(", ")
                    else:
                        self.lst.append(param + "=" + str(preset))
                        self.lst.append(", ")
                if len(node.presets) > 0:
                    self.lst.pop()
                self.lst.append(") {\n")
                self.indentation += 4
                self.new_line = True
                self.decompile_node(node.body)
                self.indentation -= 4
                self.lst.append(" " * self.indentation + "}")
            elif t == psr.FUNCTION_CALL:
                node: psr.FuncCall
                if node.f_name != "=>":
                    self.lst.append(node.f_name)
                self.lst.append("(")
                self.new_line = False
                self.call_layer += 1
                self.decompile_node(node.args)
                self.call_layer -= 1
                if self.call_layer == 0:
                    self.new_line = True
                self.lst.append(")")
                # self.new_line = True
            elif t == psr.DOT:
                node: psr.Dot
                self.decompile_node(node.left)
                self.lst.append(".")
                self.decompile_node(node.right)
            elif t == psr.CLASS_STMT:
                node: psr.ClassStmt
                self.lst.append("class ")
                self.lst.append(node.class_name)
                if len(node.superclass_names) > 0:
                    self.lst.append(" extends ")
                    for sc in node.superclass_names:
                        self.lst.append(sc)
                        self.lst.append(", ")
                    self.lst.pop()
                self.lst.append(" {\n")
                self.indentation += 4
                self.decompile_node(node.block)
                self.indentation -= 4
                self.lst.append(" " * self.indentation + "}")
            elif t == psr.CLASS_INIT:
                node: psr.ClassInit
                self.lst.append("new ")
                self.lst.append(node.class_name)
                if node.args:
                    self.lst.append("(")
                    self.new_line = False
                    self.decompile_node(node.args)
                    self.new_line = True
                    self.lst.append(")")
            elif t == psr.ABSTRACT:
                self.lst.append("abstract")
            elif t == psr.BREAK_STMT:
                self.lst.append("break")
            elif t == psr.CONTINUE_STMT:
                self.lst.append("continue")
            elif isinstance(node, psr.UnaryOperator):
                node: psr.UnaryOperator
                t = self.calculate_parenthesis(node)
                front = t[0]
                back = t[1]
                self.lst.append(node.operation)
                self.lst.append(" ")
                self.lst.append(front)
                self.decompile_node(node.value)
                self.lst.append(back)
            elif t == psr.BOOLEAN_STMT:
                node: psr.BooleanStmt
                self.lst.append(node.value)
            elif t == psr.UNDEFINED_NODE:
                self.lst.append("undefined")
            # elif t == psr.ANONYMOUS_CALL:
            #     node: psr.AnonymousCall

        else:
            self.lst.append(str(node))
