import spl_parser as psr
import os

EOF = -1
EOL = ";"
SYMBOLS = {"{", "}", ".", ","}
MIDDLE = {"(", ")", "[", "]"}
BINARY_OPERATORS = {"+": "add", "-": "sub", "*": "mul", "/": "div", "%": "mod",
                    "<": "lt", ">": "gt", "==": "eq", ">=": "ge", "<=": "le", "!=": "neq",
                    "&&": "and", "||": "or", "&": "band", "^": "xor", "|": "bor",
                    "<<": "lshift", ">>": "rshift", "===": "", "!==": "", "instanceof": ""}
UNARY_OPERATORS = {"!": "not"}
OTHERS = {"=", "@", ":"}
ALL = set().union(SYMBOLS).union(BINARY_OPERATORS).union(OTHERS).union(MIDDLE).union(UNARY_OPERATORS)
RESERVED = {"class", "function", "def", "if", "else", "new", "extends", "return", "break", "continue",
            "true", "false", "null", "operator", "while", "for", "import", "throw", "try", "catch", "finally",
<<<<<<< HEAD
            "abstract", "private", "const", "as"}
=======
            "abstract", "private"}
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
LAZY = {"&&", "||"}
OMITS = {"\n", "\r", "\t", " "}

OP_EQ = {"+", "-", "*", "/", "%", "&", "^", "|", "<<", ">>"}

ESCAPES = {"n": "\n", "t": "\t", "0": "\0", "a": "\a", "r": "\r", "f": "\f", "v": "\v", "b": "\b", "\\": "\\"}

NO_BUILD_LINE = {"else", "catch", "finally"}

PUBLIC = 0
PRIVATE = 1

SPL_PATH = os.getcwd()


class Lexer:
    """
    :type tokens: list of Token
    """

    def __init__(self):
        self.tokens = []
        self.script_dir = ""
        self.file_name = ""

    def tokenize(self, source):
        self.tokens.clear()
        if isinstance(source, list):
            self.tokenize_text(source)
        else:
            self.tokenize_file(source)

    def tokenize_file(self, file):
        """
        :type file: _io.TextIOWrapper
        :param file:
        :return:
        """
        line = file.readline()
        line_num = 1
        in_doc = False
        while line:
            tup = (line_num, self.file_name)
            last_index = len(self.tokens)
            in_doc = self.proceed_line(line, tup, in_doc)
            # print(self.tokens[last_index:])
            self.find_import(tup, last_index, len(self.tokens))
            line = file.readline()
            line_num += 1

        self.tokens.append(Token((EOF, self.file_name)))

    def tokenize_text(self, lines):
        for i in range(len(lines)):
            line_number = i + 1
            line = lines[i]
            self.proceed_line(line, (line_number, "console"), False)

        self.tokens.append(Token((EOF, self.file_name)))

    def proceed_line(self, line: str, line_num: (int, str), in_doc):
        """ Tokenize a line.

        :param line: line to be proceed
        :param line_num: the line number and the name of source file
        :param in_doc: whether it is currently in docstring, before proceed this line
        :return: whether it is currently in docstring, after proceed this line
        """
        in_single = False
        in_double = False
        literal = ""
        non_literal = ""
        # last_ch = ""

        length = len(line)
        i = -1
        while i < length - 1:
            i += 1
            ch = line[i]
            if not in_double and not in_single:
                if in_doc:
                    if ch == "*" and i < length - 1 and line[i + 1] == "/":
                        in_doc = False
                        i += 2
                        continue
                else:
                    if ch == "/" and i < length - 1 and line[i + 1] == "*":
                        in_doc = True
                        i += 1

            if not in_doc:
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
                    if len(non_literal) > 1 and non_literal[-2:] == "//":
                        self.line_tokenize(non_literal[:-2], line_num)
                        non_literal = ""
                        break

        if len(non_literal) > 0:
            self.line_tokenize(non_literal, line_num)

        return in_doc

    def line_tokenize(self, non_literal, line_num):
        """
        Tokenize a line, with string literals removed.

        :param non_literal: text to be tokenize, no string literal
        :param line_num: the line number and the name of source file
        :return: None
        """
        lst = normalize(non_literal)
        for part in lst:
            # if part == "//":
            #     break
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
            elif part[:-1] in OP_EQ:
                self.tokens.append(IdToken(line_num, part))
            elif part == EOL:
                self.tokens.append(IdToken(line_num, EOL))
            elif part == "=>":
                self.tokens.append(IdToken(line_num, part))
            elif part in OMITS:
                pass
            else:
                raise ParseException("Unknown symbol: '{}', at line {}".format(part, line_num))

    def find_import(self, line_file, from_, to):
        """
        Finds import statement from tokenized list.

        :param line_file: the line number and source file name
        :param from_: the beginning index of finding
        :param to: the end index of finding
        :return: None
        """
        for i in range(from_, to, 1):
            token = self.tokens[i]
            if isinstance(token, IdToken) and token.symbol == "import":
                next_token: LiteralToken = self.tokens[i + 1]
                name = next_token.text
                import_name = None
                if i + 3 < to:
                    as_token = self.tokens[i + 2]
                    if isinstance(as_token, IdToken) and as_token.symbol == "as":
                        name_token: IdToken = self.tokens[i + 3]
                        import_name = name_token.symbol
                        self.tokens.pop(i)
                        self.tokens.pop(i)
                self.tokens.pop(i)
                self.tokens.pop(i)
                if name[-3:] == ".sp":
                    # user lib
                    file_name = "{}{}{}".format(self.script_dir, os.sep, name)
                    no_sp_name = name[:-3]
                else:
                    # system lib
                    file_name = "{}{}lib{}{}.sp".format(SPL_PATH, os.sep, os.sep, name)
                    no_sp_name = name

                if import_name is None:
                    import_name = no_sp_name.replace("/", "\\")
                self.import_file(line_file, file_name, import_name)
                # print(self.tokens)
                break

    def import_file(self, line_file, full_path, import_name):
        """
        Imports a full script file into the tokens list.

        :param line_file: the line number and the source file name
        :param full_path: the full path of the imported file.
        :param import_name: the name of the module
        :return: None
        """
        file = open(full_path, "r")
        lexer = Lexer()
        lexer.file_name = full_path
        lexer.script_dir = get_dir(full_path)
        lexer.tokenize(file)
        # print(lexer.tokens)
        self.tokens.append(IdToken(line_file, "import"))
        self.tokens.append(IdToken(line_file, import_name))
        self.tokens.append(IdToken(line_file, "{"))
        self.tokens += lexer.tokens
        self.tokens.pop()  # remove the EOF token
        self.tokens.append(IdToken(line_file, "}"))
        self.tokens.append(IdToken(line_file, EOL))
        file.close()

    def parse(self):
        """
        :rtype: psr.Parser
        :return: the parsed block
        :rtype: psr.BlockStmt
        """
        parser = psr.Parser()
        i = 0
        func_count = 0
        in_cond = False
        auth = PUBLIC
        call_nest = 0
        brace_count = 0
        class_braces: [(int, bool)] = []  # records the brace count when class stmt starts, True if is class, False
        # if is import
        extra_precedence = 0

        while True:
            try:
                token = self.tokens[i]
                line = (token.line_number(), token.file_name())
                if isinstance(token, IdToken):
                    sym = token.symbol
                    if sym == "if":
                        in_cond = True
                        parser.add_if(line)
                        i += 1
                        next_token = self.tokens[i]
                        if not (isinstance(next_token, IdToken) and next_token.symbol == "("):
                            unexpected_token(token)
                    elif sym == "while":
                        in_cond = True
                        parser.add_while(line)
                        i += 1
                    elif sym == "for":
                        in_cond = True
                        parser.add_for_loop(line)
                        i += 1
                    elif sym == "else":
                        pass  # this case is automatically handled by the if-block
                    elif sym == "return":
                        parser.add_return(line)
                        # in_expr = True
                        # expr_layer += 1
                    elif sym == "break":
                        parser.add_break(line)
                    elif sym == "continue":
                        parser.add_continue(line)
                    elif sym == "true" or sym == "false":
                        parser.add_bool(line, sym)
                    elif sym == "null":
                        parser.add_null(line)
                    elif sym == "@":
                        i += 1
                    elif sym == "{":
                        brace_count += 1
                        parser.new_block()
                    elif sym == "}":
                        brace_count -= 1
                        parser.build_line()
                        parser.build_block()
                        if len(class_braces) > 0 and brace_count == class_braces[-1][0]:
                            if class_braces[-1][1]:
                                parser.build_class()
                            else:
                                parser.build_import()
                            class_braces.pop()
                        next_token = self.tokens[i + 1]
                        if not (isinstance(next_token, IdToken) and next_token.symbol in NO_BUILD_LINE):
                            parser.build_expr()
                            parser.build_line()
                    elif sym == "(":
                        extra_precedence += 1
                    elif sym == ")":
                        if extra_precedence == 0:
                            if call_nest > 0:
                                # parser.build_expr()
                                parser.build_line()
                                parser.build_call()
                                call_nest -= 1
                            elif in_cond:
                                parser.build_expr()
                                parser.build_condition()
                                in_cond = False
                        else:
                            # if parser.in_expr:
                            extra_precedence -= 1
                    elif sym == "]":
                        next_token = self.tokens[i + 1]
                        if isinstance(next_token, IdToken) and next_token.symbol == "=":
                            parser.build_get_set(True)
                            parser.build_line()
                            i += 1
                        else:
                            parser.build_get_set(False)
                            parser.build_line()
                            parser.build_call()
                            call_nest -= 1
                    elif sym == "=":
                        parser.build_expr()
                        parser.add_assignment(line)
                    elif sym == ":":
                        parser.build_expr()
                        parser.add_type(line)
                    elif sym == ",":
                        parser.build_expr()
                        if call_nest > 0:
                            parser.build_line()
                    elif sym == ".":
                        parser.add_dot(line, extra_precedence)
                    elif sym == "=>":
                        parser.add_anonymous_call(line, extra_precedence)
                        i += 1
                        call_nest += 1
                    elif sym == "function" or sym == "def":
                        i += 1
                        f_token: IdToken = self.tokens[i]
                        f_name = f_token.symbol
<<<<<<< HEAD
                        res = parse_def(f_name, self.tokens, i, func_count, parser, auth, is_const)
=======
                        res = parse_def(f_name, self.tokens, i, func_count, parser, auth)
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
                        i = res[0]
                        func_count = res[1]
                        auth = PUBLIC
                    elif sym == "operator":
                        i += 1
                        op_token: IdToken = self.tokens[i]
                        op_name = "@" + BINARY_OPERATORS[op_token.symbol]
<<<<<<< HEAD
                        res = parse_def(op_name, self.tokens, i, func_count, parser, PUBLIC, False)
=======
                        res = parse_def(op_name, self.tokens, i, func_count, parser, PUBLIC)
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
                        i = res[0]
                        func_count = res[1]
                    elif sym == "import":
                        i += 1
                        next_token: IdToken = self.tokens[i]
                        import_name = next_token.symbol
                        parser.add_import(line, import_name)
                        class_braces.append((brace_count, False))
                    elif sym == "class":
                        i += 1
                        c_token: IdToken = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class((c_token.line_number(), c_token.file_name()), class_name)
                        class_braces.append((brace_count, True))
                    elif sym == "extends":
                        i += 1
                        cla = parser.get_current_class()
                        while True:
                            c_token = self.tokens[i]
                            superclass_name = c_token.symbol
                            parser.add_extends(superclass_name, cla)
                            next_token = self.tokens[i + 1]
                            if isinstance(next_token, IdToken) and next_token.symbol == ",":
                                i += 2
                            else:
                                break
                    elif sym == "abstract":
                        parser.add_abstract(line)
                    elif sym == "private":
                        auth = PRIVATE
                    elif sym == "new":
                        i += 1
                        c_token = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class_new((c_token.line_number(), c_token.file_name()), class_name)
                        next_token = self.tokens[i + 1]
                        if i + 1 < len(self.tokens) and isinstance(next_token, IdToken) and \
                                next_token.symbol == "(":
                            i += 1
                            call_nest += 1
                            parser.add_call((c_token.line_number(), c_token.file_name()), class_name)
                            # in_call = True
                    elif sym == "throw":
                        parser.add_throw(line)
                    elif sym == "try":
                        parser.add_try(line)
                    elif sym == "catch":
                        parser.add_catch(line)
                        i += 1
                        in_cond = True
                    elif sym == "finally":
                        parser.add_finally(line)
                    elif sym in BINARY_OPERATORS:
                        if sym == "-" and (i == 0 or is_unary(self.tokens[i - 1])):
                            parser.add_neg(line, extra_precedence)
                        # elif sym == "*" and (i == 0 or is_unary(self.tokens[i - 1])):
                        #     parser.add_unpack(line, extra_precedence)
                        else:
                            parser.add_operator(line, sym, extra_precedence)
                    elif sym in UNARY_OPERATORS:
                        if sym == "!":
                            parser.add_not(line, extra_precedence)
                    elif sym[:-1] in OP_EQ:
                        parser.add_operator(line, sym, extra_precedence, True)
                    elif token.is_eol():
                        if parser.is_in_get():
                            # parser.build_line()
                            parser.build_call()
                            # parser.in_get = False
                            call_nest -= 1
                        parser.build_expr()
                        # print(parser.stack)
                        parser.build_line()
                    else:
                        next_token = self.tokens[i + 1]
                        if isinstance(next_token, IdToken):
                            if next_token.symbol == "(":
                                # function call
                                parser.add_call(line, sym)
                                call_nest += 1
                                i += 1
                            elif next_token.symbol == "[":
                                parser.add_name(line, sym, auth)
                                parser.add_dot(line, extra_precedence)
                                parser.add_get_set(line)
                                call_nest += 1
                                i += 1
                            else:
                                parser.add_name(line, sym, auth)
                        else:
                            parser.add_name(line, sym, auth)
                        auth = PUBLIC

                elif isinstance(token, NumToken):
                    value = token.value
                    parser.add_number(line, value)
                elif isinstance(token, LiteralToken):
                    value = token.text
                    parser.add_literal(line, value)
                elif token.is_eof():
                    parser.build_line()
                    break
                else:
                    unexpected_token(token)
                i += 1
            except Exception:
                raise ParseException("Parse error in '{}', at line {}".format(self.tokens[i].file_name(),
                                                                              self.tokens[i].line_number()))

        if in_cond or call_nest != 0 or brace_count != 0 or extra_precedence != 0:
            raise ParseException("Reach the end while parsing")
        return parser.get_as_block()


def unexpected_token(token):
    if isinstance(token, IdToken):
        raise ParseException("Unexpected token: '{}', in {}, at line {}".format(token.symbol,
                                                                                token.file_name(),
                                                                                token.line_number()))
    else:
        raise ParseException("Unexpected token in '{}', at line {}".format(token.file_name(),
                                                                           token.line_number()))


<<<<<<< HEAD
def parse_def(f_name, tokens, i, func_count, parser: psr.Parser, auth, is_const):
=======
def parse_def(f_name, tokens, i, func_count, parser, auth):
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
    """
    Parses a function declaration into abstract syntax tree.

    :param f_name: the function name
    :param tokens: the list of all tokens
    :param i: the current reading index of the token list
    :param func_count: the count the anonymous functions
    :param parser: the Parser object
    :param auth: the authority of this function
<<<<<<< HEAD
    :param is_const: whether this defines a constant function
=======
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
    :return: tuple(new index, new anonymous function count)
    """
    tup = (tokens[i].line_number(), tokens[i].file_name())
    if f_name == "(":
<<<<<<< HEAD
        parser.add_function(tup, "af-{}".format(func_count), auth, is_const)
        # "af" stands for anonymous function
        func_count += 1
    else:
        parser.add_function(tup, f_name, auth, is_const)
=======
        parser.add_function(tup, "af-{}".format(func_count), auth)  # "af" stands for anonymous function
        func_count += 1
    else:
        parser.add_function(tup, f_name, auth)
>>>>>>> parent of 344cb36... Updated to spl 1.1.0
        i += 1
    front_par = tokens[i]
    if isinstance(front_par, IdToken) and front_par.symbol == "(":
        i += 1
        params = []
        presets = []
        ps = False
        while True:
            token = tokens[i]
            if isinstance(token, IdToken):
                sbl = token.symbol
            elif isinstance(tokens[i], NumToken):
                sbl = token.value
            else:
                sbl = token.text
            # print(str(sbl) + " " + str(ps))
            if sbl == ")":
                # i -= 1
                break
            elif sbl != ",":
                if ps:
                    ps = False
                    presets.append(token)
                elif sbl == "=":
                    ps = True
                else:
                    params.append(sbl)
            i += 1
        presets = [psr.InvalidToken(tup) for _ in range(len(params) - len(presets))] + presets
        # print(presets)
        parser.build_func_params(params, presets)
    return i, func_count


def is_unary(last_token):
    """
    Returns True iff this should be an unary operator.
    False if it should be a minus operator.

    :param last_token:
    :type last_token: Token
    :return:
    :rtype: bool
    """
    if isinstance(last_token, IdToken):
        if last_token.is_eol():
            return True
        else:
            sym = last_token.symbol
            if sym in BINARY_OPERATORS:
                return True
            elif sym in SYMBOLS:
                return True
            elif sym == "(":
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
    Splits a line to tokens.

    :type string: str
    :param string:
    :return:
    :type: list
    """
    if string.isidentifier():
        return [string]
    else:
        lst = []
        if len(string) > 0:
            s = string[0]
            last_type = char_type(s)
            self_concatenate = {0, 1, 8, 9, 10, 11, 14}
            cross_concatenate = {(8, 9), (1, 0), (0, 12), (12, 0), (15, 9), (17, 9), (16, 9), (10, 9), (11, 9),
                                 (9, 8)}
            for i in range(1, len(string), 1):
                char = string[i]
                t = char_type(char)
                if (t in self_concatenate and t == last_type) or ((last_type, t) in cross_concatenate):
                    s += char
                else:
                    put_string(lst, s)
                    s = char
                last_type = t
            put_string(lst, s)
        return lst


def put_string(lst: list, s: str):
    if len(s) > 1 and s[-1] == ".":  # Scenario of a name ended with a number.
        lst.append(s[:-1])
        lst.append(s[-1])
    else:
        lst.append(s)


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
    elif ch == ">" or ch == "<":
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
    # elif ch == "/":
    #     return 14
    elif ch == "!":
        return 15
    elif ch == "^":
        return 16
    elif ch in {"+", "-", "*", "/", "%"}:
        return 17
    elif ch == "@":
        return 18


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


def get_dir(f_name: str):
    if os.sep in f_name:
        return f_name[:f_name.find(os.sep)]
    elif "/" in f_name:
        return f_name[:f_name.find("/")]
    else:
        return ""


class LexerException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


class ParseException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
