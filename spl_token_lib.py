EOF = -1
EOL = ";"
SYMBOLS = {"{", "}", ".", ","}
MIDDLE = {"(", ")", "[", "]"}
BINARY_OPERATORS = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod",
                    "<": "lt", ">": "gt", "==": "eq", ">=": "ge", "<=": "le", "!=": "neq",
                    "&&": "and", "||": "or", "&": "band", "^": "xor", "|": "bor",
                    "<<": "lshift", ">>": "rshift", "===": "", "!==": "", "instanceof": "",
                    "and": "and", "or": "or", "is": ""}
UNARY_OPERATORS = {"!": "not", "not": "not"}
OTHERS = {"=", "@", ":"}
ALL = set().union(SYMBOLS).union(BINARY_OPERATORS).union(OTHERS).union(MIDDLE).union(UNARY_OPERATORS)
RESERVED = {"class", "function", "def", "if", "else", "new", "extends", "return", "break", "continue",
            "true", "false", "null", "operator", "while", "for", "import", "throw", "try", "catch", "finally",
            "abstract", "const", "var", "assert", "del"}
LAZY = {"&&", "||", "and", "or"}
OMITS = {"\n", "\r", "\t", " "}
OP_EQ = {"+", "-", "*", "/", "%", "&", "^", "|", "<<", ">>"}
ESCAPES = {"n": "\n", "t": "\t", "0": "\0", "a": "\a", "r": "\r", "f": "\f", "v": "\v", "b": "\b", "\\": "\\"}
NO_BUILD_LINE = {"else", "catch", "finally"}

# PUBLIC = 0
# PRIVATE = 1


def replace_escapes(text: str):
    lst = []
    in_slash = False
    for i in range(len(text)):
        ch = text[i]
        if in_slash:
            in_slash = False
            if ch in ESCAPES:
                lst.append(ESCAPES[ch])
            else:
                lst.append("\\" + ch)
        else:
            if ch == "\\":
                in_slash = True
            else:
                lst.append(ch)
    return "".join(lst)


def unexpected_token(token):
    if isinstance(token, IdToken):
        raise ParseException("Unexpected token: '{}', in {}, at line {}".format(token.symbol,
                                                                                token.file_name(),
                                                                                token.line_number()))
    else:
        raise ParseException("Unexpected token in '{}', at line {}".format(token.file_name(),
                                                                           token.line_number()))


def get_doc_name(sp_name: str):
    """
    Returns the auto-generated document name of a .sp file.

    :param sp_name:
    :return:
    """
    return sp_name[:-2] + "sdoc"


class Token:

    def __init__(self, line):
        self.line = line[0]
        self.file = line[1]

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

    def file_name(self):
        return self.file

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
    def __init__(self, line, t: str):
        Token.__init__(self, line)

        # self.text = t.encode().decode('unicode_escape').encode('utf8').decode('utf8')
        # self.text = t.encode().decode('unicode_escape')
        self.text = replace_escapes(t)

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

    def __eq__(self, other):
        return isinstance(other, IdToken) and other.symbol == self.symbol

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


class ParseEOFException(ParseException):
    def __init__(self, msg=""):
        ParseException.__init__(self, msg)
