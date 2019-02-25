import _io
import io
import spl_parser as psr
import spl_token_lib as stl
import os

SPL_PATH = os.getcwd()


class Lexer:
    """
    :type tokens: list of Token
    """

    def __init__(self):
        self.tokens = []
        self.script_dir = ""
        self.file_name = ""
        self.doc_name = ""
        self.doc_file: io.TextIOWrapper = None

    def setup(self, file_name: str, script_dir: str, doc_name: str):
        """
        Sets up the parameters of this lexer.

        The <file_name> will be recorded in tokens and ast nodes, which is used for properly displaying
        the error message, if any error occurs. This parameter does not contribute to the actual interpreting.

        The <script_dir> is used to find the importing files, which is important to run the script correctly.

        :param file_name: the name of the main script
        :param script_dir: the directory of the main script
        :param doc_name: the file to save the spl document
        :return:
        """
        self.file_name = file_name
        self.script_dir = script_dir
        self.doc_name = doc_name

    def tokenize(self, source):
        """
        Tokenize the source spl source code into a list of tokens, stored in the memory of this Lexer.

        :param source: the source code, whether an opened file or a list of lines.
        :return: None
        """
        self.tokens.clear()
        if isinstance(source, list):
            self.tokenize_text(source)
        else:
            try:
                self.doc_file = open(self.doc_name, "w")
            except IOError:
                self.doc_file = None
            self.tokenize_file(source)
            if self.doc_file is not None:
                self.doc_file.close()

    def tokenize_file(self, file: _io.TextIOWrapper):
        """
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
            self.find_import(last_index, len(self.tokens))
            line = file.readline()
            line_num += 1

        self.tokens.append(stl.Token((stl.EOF, self.file_name)))

    def tokenize_text(self, lines):
        for i in range(len(lines)):
            line_number = i + 1
            line = lines[i]
            self.proceed_line(line, (line_number, "console"), False)

        self.tokens.append(stl.Token((stl.EOF, self.file_name)))

    def proceed_line(self, line: str, line_num: (int, str), in_doc: bool):
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
        doc = ""
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
                        self.tokens.append(stl.LiteralToken(line_num, literal))
                        literal = ""
                        continue
                elif in_single:
                    if ch == "'":
                        in_single = False
                        self.tokens.append(stl.LiteralToken(line_num, literal))
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
            else:
                doc += ch

        if len(non_literal) > 0:
            self.line_tokenize(non_literal, line_num)

        if self.doc_file is not None:
            if len(doc) > 0:
                self.doc_file.write("*")
                self.doc_file.write(doc.strip("/\n *"))
            self.doc_file.write('\n')
            self.doc_file.flush()

        return in_doc

    def write_mark(self):
        """
        Writes a mark to the doc file that shows this line contains non-doc content.

        :return: None
        """
        if self.doc_file is not None:
            self.doc_file.write("+")

    def line_tokenize(self, non_literal, line_num):
        """
        Tokenize a line, with string literals removed.

        :param non_literal: text to be tokenize, no string literal
        :param line_num: the line number
        :return: None
        """
        lst = normalize(non_literal)
        wm = 0
        for part in lst:
            # if part == "//":
            #     break
            wm += 1
            if part.isidentifier():
                if part in stl.RESERVED:
                    self.tokens.append(stl.IdToken(line_num, part))
                else:
                    self.tokens.append(stl.IdToken(line_num, part))
            elif is_float(part):
                self.tokens.append(stl.NumToken(line_num, part))
            elif part.isdigit():
                self.tokens.append(stl.NumToken(line_num, part))
            elif part in stl.ALL:
                self.tokens.append(stl.IdToken(line_num, part))
            elif part[:-1] in stl.OP_EQ:
                self.tokens.append(stl.IdToken(line_num, part))
            elif part == stl.EOL:
                self.tokens.append(stl.IdToken(line_num, stl.EOL))
            elif part == "=>":
                self.tokens.append(stl.IdToken(line_num, part))
            elif part in stl.OMITS:
                wm -= 1
            else:
                raise stl.ParseException("Unknown symbol: '{}', at line {}".format(part, line_num))

        if wm > 0:
            self.write_mark()

    def find_import(self, from_, to):
        for i in range(from_, to, 1):
            token = self.tokens[i]
            if isinstance(token, stl.IdToken) and token.symbol == "import":
                next_token: stl.LiteralToken = self.tokens[i + 1]
                name = next_token.text
                self.tokens.pop(i)
                self.tokens.pop(i)
                if name[-3:] == ".sp":
                    # user lib
                    file_name = "{}{}{}".format(self.script_dir, os.sep, name)
                else:
                    # system lib
                    file_name = "{}{}lib{}{}.sp".format(SPL_PATH, os.sep, os.sep, name)

                self.import_file(file_name)
                # print(self.tokens)
                break

    def import_file(self, full_path):
        file = open(full_path, "r")
        lexer = Lexer()
        lexer.file_name = full_path
        lexer.script_dir = get_dir(full_path)
        lexer.tokenize(file)
        # print(lexer.tokens)
        self.tokens += lexer.tokens
        self.tokens.pop()  # remove the EOF token
        file.close()

    def parse(self):
        """
        Parses the list of tokens stored in this Lexer, and returns the root node of the parsed abstract syntax
        tree.

        :return: the parsed block
        """
        parser = psr.Parser()
        i = 0
        func_count = 0
        in_cond = False
        var_level = psr.ASSIGN
        # auth = stl.PUBLIC
        call_nest = 0
        brace_count = 0
        class_brace = -1
        extra_precedence = 0

        while True:
            try:
                token = self.tokens[i]
                line = (token.line_number(), token.file_name())
                if isinstance(token, stl.IdToken):
                    sym = token.symbol
                    if sym == "if":
                        in_cond = True
                        parser.add_if(line)
                        i += 1
                        next_token = self.tokens[i]
                        if not (isinstance(next_token, stl.IdToken) and next_token.symbol == "("):
                            stl.unexpected_token(token)
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
                    elif sym == "const":
                        var_level = psr.CONST
                    elif sym == "var":
                        var_level = psr.VAR
                    elif sym == "let":
                        var_level = psr.LOCAL
                    elif sym == "@":
                        i += 1
                    elif sym == "{":
                        brace_count += 1
                        parser.new_block()
                    elif sym == "}":
                        brace_count -= 1
                        parser.build_line()
                        parser.build_block()
                        if brace_count == class_brace:
                            parser.build_class()
                            class_brace = -1
                        next_token = self.tokens[i + 1]
                        if not (isinstance(next_token, stl.IdToken) and next_token.symbol in stl.NO_BUILD_LINE):
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
                        if isinstance(next_token, stl.IdToken) and next_token.symbol == "=":
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
                        parser.add_assignment(line, var_level)
                        var_level = psr.ASSIGN
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
                        f_token: stl.IdToken = self.tokens[i]
                        f_name = f_token.symbol
                        res = parse_def(f_name, self.tokens, i, func_count, parser)
                        i = res[0]
                        func_count = res[1]
                        # auth = stl.PUBLIC
                        # is_const = False
                    elif sym == "operator":
                        i += 1
                        op_token: stl.IdToken = self.tokens[i]
                        op_name = "@" + stl.BINARY_OPERATORS[op_token.symbol]
                        res = parse_def(op_name, self.tokens, i, func_count, parser)
                        i = res[0]
                        func_count = res[1]
                    elif sym == "class":
                        i += 1
                        c_token: stl.IdToken = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class((c_token.line_number(), c_token.file_name()), class_name)
                        class_brace = brace_count
                    elif sym == "extends":
                        i += 1
                        cla = parser.get_current_class()
                        while True:
                            c_token = self.tokens[i]
                            superclass_name = c_token.symbol
                            parser.add_extends(superclass_name, cla)
                            next_token = self.tokens[i + 1]
                            if isinstance(next_token, stl.IdToken) and next_token.symbol == ",":
                                i += 2
                            else:
                                break
                    elif sym == "abstract":
                        parser.add_abstract(line)
                    # elif sym == "private":
                    #     auth = stl.PRIVATE
                    elif sym == "new":
                        i += 1
                        c_token = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class_new((c_token.line_number(), c_token.file_name()), class_name)
                        next_token = self.tokens[i + 1]
                        if i + 1 < len(self.tokens) and isinstance(next_token, stl.IdToken) and \
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
                    elif sym in stl.BINARY_OPERATORS:
                        if sym == "-" and (i == 0 or is_unary(self.tokens[i - 1])):
                            parser.add_neg(line, extra_precedence)
                        # elif sym == "*" and (i == 0 or is_unary(self.tokens[i - 1])):
                        #     parser.add_unpack(line, extra_precedence)
                        else:
                            parser.add_operator(line, sym, extra_precedence)
                    elif sym in stl.UNARY_OPERATORS:
                        if sym == "!":
                            parser.add_not(line, extra_precedence)
                    elif sym[:-1] in stl.OP_EQ:
                        parser.add_operator(line, sym, extra_precedence, True)
                    elif token.is_eol():
                        if parser.is_in_get():
                            # parser.build_line()
                            parser.build_call()
                            # parser.in_get = False
                            call_nest -= 1
                        parser.build_expr()
                        if var_level != psr.ASSIGN:
                            active = parser.get_active()
                            und_vars = active.stack.copy()
                            # print(und_vars)
                            active.stack.clear()
                            for node in und_vars:
                                active.stack.append(node)
                                parser.add_assignment(line, var_level)
                                parser.add_undefined(line)
                                parser.build_line()
                            var_level = psr.ASSIGN
                        parser.build_line()
                    else:
                        next_token = self.tokens[i + 1]
                        if isinstance(next_token, stl.IdToken):
                            if next_token.symbol == "(":
                                # function call
                                parser.add_call(line, sym)
                                call_nest += 1
                                i += 1
                            elif next_token.symbol == "[":
                                parser.add_name(line, sym)
                                parser.add_dot(line, extra_precedence)
                                parser.add_get_set(line)
                                call_nest += 1
                                i += 1
                            else:
                                parser.add_name(line, sym)
                        else:
                            parser.add_name(line, sym)
                        # auth = stl.PUBLIC

                elif isinstance(token, stl.NumToken):
                    value = token.value
                    parser.add_number(line, value)
                elif isinstance(token, stl.LiteralToken):
                    value = token.text
                    parser.add_literal(line, value)
                elif token.is_eof():
                    parser.build_line()
                    break
                else:
                    stl.unexpected_token(token)
                i += 1
            except Exception:
                raise stl.ParseException("Parse error in '{}', at line {}".format(self.tokens[i].file_name(),
                                                                                  self.tokens[i].line_number()))

        if in_cond or call_nest != 0 or brace_count != 0 or extra_precedence != 0:
            raise stl.ParseEOFException("Reach the end while parsing")
        return parser.get_as_block()


def parse_def(f_name, tokens, i, func_count, parser: psr.Parser):
    """
    Parses a function declaration into abstract syntax tree.

    :param f_name: the function name
    :param tokens: the list of all tokens
    :param i: the current reading index of the token list
    :param func_count: the count the anonymous functions
    :param parser: the Parser object
    # :param auth: the authority of this function
    :return: tuple(new index, new anonymous function count)
    """
    tup = (tokens[i].line_number(), tokens[i].file_name())
    if f_name == "(":
        parser.add_function(tup, "af-{}".format(func_count))
        # "af" stands for anonymous function
        func_count += 1
    else:
        parser.add_function(tup, f_name)
        i += 1
    front_par = tokens[i]
    if isinstance(front_par, stl.IdToken) and front_par.symbol == "(":
        i += 1
        params = []
        presets = []
        ps = False
        while True:
            token = tokens[i]
            if isinstance(token, stl.IdToken):
                sbl = token.symbol
            elif isinstance(tokens[i], stl.NumToken):
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
    if isinstance(last_token, stl.IdToken):
        if last_token.is_eol():
            return True
        else:
            sym = last_token.symbol
            if sym in stl.BINARY_OPERATORS:
                return True
            elif sym in stl.SYMBOLS:
                return True
            elif sym == "(":
                return True
            elif sym == "=":
                return True
            elif sym in stl.RESERVED:
                return True
            else:
                return False
    elif isinstance(last_token, stl.NumToken):
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
    elif ch == ":":
        return 19


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


def get_dir(f_name: str):
    if os.sep in f_name:
        return f_name[:f_name.find(os.sep)]
    elif "/" in f_name:
        return f_name[:f_name.find("/")]
    else:
        return ""
