import spl_parser as psr

EOF = -1
EOL = ";"
BINARY_OPERATORS = {"+", "-", "*", "/", "%", "<", ">", "==", ">=", "<=", "!=", "&&", "||"}


class Lexer:
    """
    :type file: _io.TextIOWrapper
    :type tokens: list of Token
    """

    def __init__(self, f):
        self.file = f
        self.reserved = {"function", "if", "else"}
        self.symbols = {"(", ")", "{", "}", "=", "+", "-", "*", "/", "%", "==",
                        "<", ">", ">=", "<=", "!=", "&&", "||", ","}
        self.tokens = []

    def read(self):
        self.tokens.clear()
        line = self.file.readline()
        line_num = 1
        while line:
            # print(line)
            lst1 = list(filter(lambda st: len(st) > 0, line.split(" ")))
            lst2 = []
            for s in lst1:
                for x in normalize(s):
                    lst2.append(x)
            # print(lst2)
            for part in lst2:
                if part.isidentifier():
                    if part in self.reserved:
                        self.tokens.append(IdToken(line_num, part))
                    else:
                        self.tokens.append(IdToken(line_num, part))
                elif part.isdigit():
                    self.tokens.append(NumToken(line_num, part))
                elif part in self.symbols:
                    self.tokens.append(IdToken(line_num, part))
                elif part == EOL:
                    self.tokens.append(IdToken(line_num, EOL))

            line = self.file.readline()
            line_num += 1

        self.tokens.append(Token(EOF))

    def parse(self):
        """
        :rtype: psr.Parser
        :return:
        """
        parser = psr.Parser()
        i = 0
        in_expr = False
        in_cond = False
        in_call = False
        while True:
            try:
                token = self.tokens[i]
                if isinstance(token, IdToken):
                    sym = token.symbol
                    if sym == "function":
                        f_token: IdToken = self.tokens[i + 1]
                        f_name = f_token.symbol
                        parser.add_function(f_name)
                        i += 2
                        front_par = self.tokens[i]
                        if isinstance(front_par, IdToken) and front_par.symbol == "(":
                            i += 1
                            params = []
                            while isinstance(self.tokens[i], IdToken) and self.tokens[i].symbol != ")":
                                sbl = self.tokens[i].symbol
                                if sbl != ",":
                                    params.append(sbl)
                                i += 1
                            parser.build_func_params(params)
                    elif sym == "if":
                        in_cond = True
                        parser.add_if()
                        i += 1
                        if not (isinstance(self.tokens[i], IdToken) and self.tokens[i].symbol == "("):
                            raise ParseException("Unexpected token at line {}".format(self.tokens[i].line_number()))
                    elif sym == "while":
                        in_cond = True
                        parser.add_while()
                        i += 1
                        if not (isinstance(self.tokens[i], IdToken) and self.tokens[i].symbol == "("):
                            raise ParseException("Unexpected token at line {}".format(self.tokens[i].line_number()))
                    elif sym == "else":
                        pass
                    elif sym == "{":
                        parser.new_block()
                    elif sym == "}":
                        # parser.build_line()
                        parser.build_block()
                    elif sym == ")":
                        if in_cond:
                            if in_expr:
                                parser.build_expr()
                                in_expr = False
                            parser.build_condition()
                            in_cond = False
                        elif in_call:
                            parser.build_call()
                            in_call = False
                    elif sym == "=":
                        parser.add_assignment()
                    elif sym == ",":
                        if in_expr:
                            parser.build_expr()
                            in_expr = False
                    elif sym in BINARY_OPERATORS:
                        parser.add_operator(sym)
                        in_expr = True
                    elif token.is_eol():
                        if in_expr:
                            parser.build_expr()
                            in_expr = False
                        parser.build_line()
                    else:
                        if isinstance(self.tokens[i + 1], IdToken) and self.tokens[i + 1].symbol == "(":
                            # function call
                            parser.add_call(sym)
                            i += 1
                            in_call = True
                        else:
                            parser.add_name(sym)

                elif isinstance(token, NumToken):
                    value = token.value
                    parser.add_number(value)
                elif isinstance(token, LiteralToken):
                    pass
                elif token.is_eof():
                    # parser.build_line()
                    break
                i += 1
            except Exception:
                raise ParseException("Parse error at line {}".format(self.tokens[i].line_number()))

        return parser


def normalize(string):
    """
    :type string: str
    :param string:
    :return:
    :type: list
    """
    if string.isidentifier():
        return [string]
    else:
        lst = []
        s = string[0]
        last_type = char_type(s)
        for i in range(1, len(string), 1):
            char = string[i]
            t = char_type(char)
            if t == last_type or (last_type == 8 and t == 9):
                s += char
            else:
                lst.append(s)
                s = char
            last_type = t
        lst.append(s)
        return lst


def char_type(ch):
    """
    :type ch: string
    :param ch:
    :return:
    """
    if ch.isdigit():
        return 0
    elif ch.isidentifier():
        return 1
    elif ch == "{":
        return 2
    elif ch == "}":
        return 3
    elif ch == "(":
        return 4
    elif ch == ")":
        return 5
    elif ch == ";":
        return 6
    elif ch == "\n":
        return 7
    elif ch == ">" or ch == "<" or ch == "!":
        return 8
    elif ch == "=":
        return 9
    elif ch == "&":
        return 10
    elif ch == "|":
        return 11
    elif ch == ".":
        return 12
    elif ch == ",":
        return 13


class Token:

    def __init__(self, line):
        self.line = line

    def __str__(self):
        if self.is_eof():
            return "EOF"
        else:
            raise LexerException("Not Implemented")

    def __repr__(self):
        return self.__str__()

    def is_eof(self):
        return self.line == EOF

    def is_eol(self):
        return False

    def is_number(self):
        return False

    def is_literal(self):
        return False

    def is_identifier(self):
        return False

    def line_number(self):
        return self.line


class NumToken(Token):
    def __init__(self, line, v):
        Token.__init__(self, line)

        self.value = v

    def is_number(self):
        return True

    def __str__(self):
        return "NumToken({})".format(self.value)

    def __repr__(self):
        return self.__str__()


class LiteralToken(Token):
    def __init__(self, line, t):
        Token.__init__(self, line)

        self.text = t

    def is_literal(self):
        return True


class IdToken(Token):
    def __init__(self, line, s):
        Token.__init__(self, line)

        self.symbol = s

    def is_identifier(self):
        return True

    def is_eol(self):
        return self.symbol == ";"

    def __str__(self):
        if self.is_eol():
            return "Id(EOL)"
        else:
            return "Id({})".format(self.symbol)

    def __repr__(self):
        return self.__str__()


class LexerException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


class ParseException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
