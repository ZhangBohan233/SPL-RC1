from typing import BinaryIO

import spl_parser as psr
import struct


BYTE_CODE_VERSION = 2

NODE_FLAG = 0
LIST_FLAG = 1
INT_FLAG = 2
FLOAT_FLAG = 3
STR_FLAG = 4
METHOD_FLAG = 5
NONE_FLAG = 6


class Coder:
    out: BinaryIO

    def __init__(self, ast: psr.BlockStmt, out):
        self.ast = ast
        self.out = out

    def code(self):
        self.write_int(BYTE_CODE_VERSION, 2)  # records the byte-code version
        self.code_in(self.ast)

    def write_int(self, number: int, length):
        b = number.to_bytes(length, "big", signed=True)
        self.out.write(b)

    def write_float(self, value: float):
        b = bytes(struct.pack("d", value))
        assert len(b) == 8
        self.out.write(b)

    def write_literal(self, lit: str):
        byt = lit.encode("utf-8")
        length = len(byt)
        self.write_int(length, 4)
        self.out.write(byt)

    def code_in(self, node):
        if node is None:
            # print(123)
            self.write_int(NONE_FLAG, 1)
        elif isinstance(node, psr.Node):
            self.write_int(NODE_FLAG, 1)  # flag for a node
            self.write_literal(type(node).__name__)
            attrs = list(filter(lambda a: a[:2] != "__" and a[-2:] != "__", dir(node)))
            for attr in attrs:
                # self.write_literal(attr)
                value = getattr(node, attr)
                self.code_in(value)
        elif isinstance(node, list):
            self.write_int(LIST_FLAG, 1)
            self.write_int(len(node), 4)
            for item in node:
                self.code_in(item)
        elif isinstance(node, int):
            self.write_int(INT_FLAG, 1)
            self.write_int(node, 8)
        elif isinstance(node, float):
            self.write_int(FLOAT_FLAG, 1)
            self.write_float(node)
        elif isinstance(node, str):
            self.write_int(STR_FLAG, 1)
            self.write_literal(node)
        elif type(node).__name__ == "method":
            self.write_int(METHOD_FLAG, 1)
        else:
            raise CoderException(type(node).__name__)


class Decoder:
    in_file: BinaryIO

    def __init__(self, in_file):
        self.in_file = in_file

    def decode(self) -> psr.BlockStmt:
        bcv = self.read_int(2)
        if bcv != BYTE_CODE_VERSION:
            raise CoderException("Unsupported byte-code version")
        return self.decode_in()

    def read_int(self, length) -> int:
        b = self.in_file.read(length)
        return int.from_bytes(b, "big", signed=True)

    def read_float(self):
        b = self.in_file.read(8)
        return struct.unpack("d", b)

    def read_literal(self) -> str:
        length = self.read_int(4)
        b = self.in_file.read(length)
        return b.decode("utf-8")

    def decode_in(self):
        flag = self.read_int(1)
        if flag == NONE_FLAG:
            return None
        elif flag == NODE_FLAG:
            node_type = self.read_literal()
            # print(node_type)
            node = eval("psr." + node_type)
            instance = node.__new__(node)

            attrs = list(filter(lambda a: a[:2] != "__" and a[-2:] != "__", dir(node)))
            for attr in attrs:
                setattr(instance, attr, self.decode_in())
            return instance
        elif flag == LIST_FLAG:
            length = self.read_int(4)
            lst = []
            for i in range(length):
                lst.append(self.decode_in())
            return lst
        elif flag == INT_FLAG:
            return self.read_int(8)
        elif flag == FLOAT_FLAG:
            return self.read_float()
        elif flag == STR_FLAG:
            return self.read_literal()
        elif flag == METHOD_FLAG:
            return None
        else:
            raise CoderException("Unknown flag")


class CoderException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
