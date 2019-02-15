import _io
from spl_parser import *
from spl_lib import *
import spl_interpreter as itr


class VirtualMachine:
    def __init__(self, argv):
        self.byt: bytes = None
        self.env = Environment(True, {})
        self.env.add_heap("system", System(argv, "utf8"))
        self.env.scope_name = "Global"

        self.index = 0
        self.byt_len = 0

        self.root = BlockStmt((0, "compiler"))

    def set_file(self, f):
        self.byt = f.read()
        self.byt_len = len(self.byt)

    def restore_tree(self):
        # result = 0
        # while self.index < self.byt_len:
        #     result = self.vm_evaluate(self.root)
        # return result
        tree = self.vm_evaluate()
        return tree

    def read_int(self, length):
        seq = self.byt[self.index: self.index + length]
        i = int.from_bytes(seq, "big", signed=True)
        self.index += length
        return i

    def read_float(self, length):
        return 0.0

    def read_literal(self):
        length = self.read_int(4)
        seq = self.byt[self.index: self.index + length]
        self.index += length
        return seq.decode(encoding="utf8")

    def vm_evaluate(self):
        if self.index < self.byt_len:
            flag = self.read_int(1)
            line_num = self.read_int(4)
            file = self.read_literal()
            lf = (line_num, file)
            if flag == -1:
                return None
            elif flag == INT_NODE:
                return self.read_int(8)
            elif flag == FLOAT_NODE:
                return self.read_float(8)
            elif flag == LITERAL_NODE:
                return String(self.read_literal())
            elif flag == NAME_NODE:
                auth = self.read_int(1)
                name = self.read_literal()
                node = NameNode(lf, name, auth)
                return node
            elif flag == BOOLEAN_STMT:
                bv = self.read_int(1)
                if bv == 0:
                    return FALSE
                else:
                    return TRUE
            elif flag == NULL_STMT:
                pass
            elif flag == BREAK_STMT:
                pass
            elif flag == CONTINUE_STMT:
                pass
            elif flag == ASSIGNMENT_NODE:
                return self.assignment(lf)
            elif flag == DOT:
                pass
                # pre = self.read_int(1) * MULTIPLIER
                # left = self.vm_evaluate(env)
                # right = self.vm_evaluate(env)
            elif flag == ANONYMOUS_CALL:
                pass
            elif flag == OPERATOR_NODE:
                # pre = self.read_int(1) * MULTIPLIER
                op = self.read_literal()
                left = self.vm_evaluate()
                right = self.vm_evaluate()
                opn = OperatorNode(lf, 0)
                opn.operation = op
                opn.left = left
                opn.right = right
                return opn
            elif flag == NEGATIVE_EXPR:
                pass
            elif flag == NOT_EXPR:
                pass
            elif flag == RETURN_STMT:
                pass
                # value = self.vm_evaluate(env)
                # env.terminate(value)
                # return value
            elif flag == BLOCK_STMT:
                length = self.read_int(4)
                bs = BlockStmt(lf)
                for i in range(length):
                    result = self.vm_evaluate()
                    bs.lines.append(result)
                return bs
            elif flag == IF_STMT:
                pass
            elif flag == WHILE_STMT:
                condition = self.vm_evaluate()
                body = self.vm_evaluate()
                loop = WhileStmt(lf)
                loop.condition = condition
                loop.body = body
                return loop
            elif flag == FOR_LOOP_STMT:
                pass
            elif flag == DEF_STMT:
                pass
                # auth = self.read_int(1)
                # f_name = self.read_literal()
                # param_num = self.read_int(4)
                # params = []
                # presets = []
                # for i in range(param_num):
                #     params[i] = self.read_literal()
                # for i in range(param_num):
                #     presets[i] = self.vm_evaluate(env)
                # body = self.vm_evaluate(env)
                # f = Function(params, presets, body)
                # f.outer_scope = env
                # env.assign(f_name, f)
                # if auth == lex.PRIVATE:
                #     env.add_private(f_name)
                # return f
            elif flag == FUNCTION_CALL:
                pass
                # gs = self.read_int(1)
                # f_name = self.read_literal()
                # args = self.vm_evaluate(env)

    def assignment(self, lf):
        tpe = self.read_int(1)
        if tpe == 0:
            name = self.read_literal()
            value = self.vm_evaluate()
            asn = AssignmentNode(lf)
            asn.left = NameNode(lf, name, lex.PUBLIC)
            asn.right = value
            return asn
        else:
            pass


def arithmetic(left, right, symbol, env):
    if isinstance(left, int) or isinstance(left, float):
        return itr.num_arithmetic(left, right, symbol)
