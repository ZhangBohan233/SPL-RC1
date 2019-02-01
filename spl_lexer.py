import spl_parser as psr

EOF = -1
EOL = ";"
SYMBOLS = {"{", "}", ".", ","}
MIDDLE = {"(", ")"}
BINARY_OPERATORS = {"+", "-", "*", "/", "%", "<", ">", "==", ">=", "<=", "!=", "&&", "||"}
OTHERS = {"="}
ALL = set().union(SYMBOLS).union(BINARY_OPERATORS).union(OTHERS).union(MIDDLE)
RESERVED = {"class", "function", "if", "else", "new", "extends"}
OMITS = {"\n", "\r", "\t", " "}


class Lexer:
    """
    :type file: _io.TextIOWrapper
    :type tokens: list of Token
    """

    def __init__(self, f):
        self.file = f
        self.tokens = []

    def tokenize(self):
        self.tokens.clear()
        line = self.file.readline()
        line_num = 1
        while line:
            self.proceed_line(line, line_num)

            line = self.file.readline()
            line_num += 1

        self.tokens.append(Token(EOF))

    def proceed_line(self, line, line_num):
        """

        :param line: line to be proceed
        :param line_num: the line number
        :type line: str
        :return:
        """
        in_single = False
        in_double = False
        literal = ""
        non_literal = ""
        # lst = []
        for ch in line:
            if in_double:
                if ch == '"':
                    in_double = False
                    self.tokens.append(LiteralToken(line_num, literal))
                    literal = ""
                    continue
            elif in_single:
                if ch == "'":
                    in_single = False
                    self.tokens.append(LiteralToken(line_num, literal))
                    literal = ""
                    continue
            else:
                if ch == '"':
                    in_double = True
                    self.line_tokenize(non_literal, line_num)
                    non_literal = ""
                    continue
                elif ch == "'":
                    in_single = True
                    self.line_tokenize(non_literal, line_num)
                    non_literal = ""
                    continue
            if in_single or in_double:
                literal += ch
            else:
                non_literal += ch

        if len(non_literal) > 0:
            self.line_tokenize(non_literal, line_num)

    def line_tokenize(self, non_literal, line_num):
        lst = normalize(non_literal)
        for part in lst:
            if part == "//":
                break
            if part.isidentifier():
                if part in RESERVED:
                    self.tokens.append(IdToken(line_num, part))
                else:
                    self.tokens.append(IdToken(line_num, part))
            elif is_float(part):
                self.tokens.append(NumToken(line_num, part))
            elif part.isdigit():
                self.tokens.append(NumToken(line_num, part))
            elif part in ALL:
                self.tokens.append(IdToken(line_num, part))
            elif part == EOL:
                self.tokens.append(IdToken(line_num, EOL))
            elif part in OMITS:
                pass
            else:
                raise ParseException("Unknown symbol: '{}', at line {}".format(part, line_num))

    def pre_arrange(self):
        lst = []
        count = 0
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            if i < len(self.tokens) - 1:
                next_token = self.tokens[i + 1]
                if isinstance(token, IdToken) and isinstance(next_token, IdToken):
                    if token.symbol == ")" and next_token.symbol == "(":
                        lst.append(IdToken(token.line_number(), EOL))
                        var = []
                        if i > 1 and isinstance(self.tokens[i - 1], IdToken) and self.tokens[i - 1].symbol == "=":
                            # var = []
                            while len(lst) > 0 and not lst[-1].is_eol():
                                var.append(lst.pop())
                            var.reverse()

    def parse(self):
        """
        :rtype: psr.Parser
        :return:
        """
        parser = psr.Parser()
        i = 0
        func_count = 0
        in_expr = False
        in_call_expr = False
        in_cond = False
        in_call = False
        # in_continue_call = False
        brace_count = 0
        class_brace = -1
        extra_precedence = 0
        while True:
            try:
                token = self.tokens[i]
                if isinstance(token, IdToken):
                    sym = token.symbol
                    if sym == "function":
                        i += 1
                        f_token = self.tokens[i]
                        f_name = f_token.symbol
                        if f_name == "(":
                            parser.add_function("af-{}".format(func_count))  # "af" stands for anonymous function
                            func_count += 1
                        else:
                            parser.add_function(f_name)
                            i += 1
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
                    elif sym == "class":
                        i += 1
                        c_token = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class(class_name)
                        class_brace = brace_count
                    elif sym == "extends":
                        i += 1
                        c_token = self.tokens[i]
                        superclass_name = c_token.symbol
                        parser.add_extends(superclass_name)
                    elif sym == "new":
                        i += 1
                        c_token = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class_new(class_name)
                        if i + 1 < len(self.tokens) and isinstance(self.tokens[i + 1], IdToken) and \
                                self.tokens[i + 1].symbol == "(":
                            i += 1
                            in_call = True
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
                        brace_count += 1
                        parser.new_block()
                    elif sym == "}":
                        brace_count -= 1
                        # parser.build_line()
                        parser.build_block()
                        if brace_count == class_brace:
                            parser.build_class()
                            class_brace = -1
                    elif sym == "(":
                        # if i > 0 and isinstance(self.tokens[i - 1], IdToken) and self.tokens[i - 1].symbol == ")":
                        #     parser.add_continue_call(extra_precedence)
                        #     # in_expr = True
                        #     in_continue_call = True
                        #     in_call = True
                        if in_expr:
                            extra_precedence += 1
                    elif sym == ")":
                        if extra_precedence == 0:
                            if in_cond:
                                if in_expr:
                                    parser.build_expr()
                                    in_expr = False
                                parser.build_condition()
                                in_cond = False
                            elif in_call:
                                if in_call_expr:
                                    parser.build_call_expr()
                                    in_call_expr = False
                                parser.build_call()
                                if in_expr:
                                    parser.build_expr()
                                    in_expr = False
                                # parser.build_call()
                                in_call = False
                        else:
                            if in_expr:
                                extra_precedence -= 1
                    elif sym == "=":
                        parser.build_expr()
                        parser.add_assignment()
                    elif sym == ",":
                        if in_expr:
                            parser.build_expr()
                            in_expr = False
                    elif sym == ".":
                        parser.add_dot(extra_precedence)
                        in_expr = True
                        if in_call:
                            in_call_expr = True
                    elif sym in BINARY_OPERATORS:
                        if sym == "-" and (i == 0 or is_neg(self.tokens[i - 1])):
                            parser.add_neg(extra_precedence)
                        else:
                            parser.add_operator(sym, extra_precedence)
                        in_expr = True
                        if in_call:
                            in_call_expr = True
                    elif token.is_eol():
                        if in_expr:
                            parser.build_expr()
                            in_expr = False
                        parser.build_line()
                    else:
                        if isinstance(self.tokens[i + 1], IdToken) and self.tokens[i + 1].symbol == "(":
                            # function call
                            parser.add_call(sym)
                            # print("call " + self.tokens[i].symbol + str(self.tokens[i].line_number()))
                            i += 1
                            in_call = True
                        else:
                            parser.add_name(sym)

                elif isinstance(token, NumToken):
                    value = token.value
                    parser.add_number(value)
                elif isinstance(token, LiteralToken):
                    value = token.text
                    parser.add_literal(value)
                elif token.is_eof():
                    # parser.build_line()
                    break
                else:
                    raise ParseException("Unexpected token at line {}".format(self.tokens[i].line_number()))
                i += 1
            except Exception:
                raise ParseException("Parse error at line {}".format(self.tokens[i].line_number()))

        return parser


def is_neg(last_token):
    """
    Returns True iff this should be a negation unary operator.
    False if it should be a minus operator.

    :param last_token:
    :type last_token: Token
    :return:
    :rtype: bool
    """
    # 大三角
    if isinstance(last_token, IdToken):
        if last_token.is_eol():
            return True
        else:
            sym = last_token.symbol
            if sym in BINARY_OPERATORS:
                return True
            elif sym == "=":
                return True
            elif sym in RESERVED:
                return True
            else:
                return False
    elif isinstance(last_token, NumToken):
        return False
    else:
        return True


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
        self_concatenate = {0, 1, 9, 10, 11, 14}
        cross_concatenate = {(8, 9), (1, 0), (0, 12), (12, 0)}
        for i in range(1, len(string), 1):
            char = string[i]
            t = char_type(char)
            if (t in self_concatenate and t == last_type) or ((last_type, t) in cross_concatenate):
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
    elif ch == "/":
        return 14


def is_float(num_str):
    """
    :type num_str: str
    :param num_str:
    :return:
    """
    if "." in num_str:
        index = num_str.index(".")
        front = num_str[:index]
        back = num_str[index + 1:]
        if len(front) > 0:
            if not front.isdigit():
                return False
        if back.isdigit():
            return True
    return False


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

    def __str__(self):
        return "LIT({})".format(self.text)

    def __repr__(self):
        return self.__str__()


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
