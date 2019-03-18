import _io
import io
import spl_token_lib as stl
import os

SPL_PATH = os.getcwd()

SELF_CONCATENATE = {0, 1, 8, 9, 10, 11, 14}
CROSS_CONCATENATE = {(8, 9), (1, 0), (0, 12), (12, 0), (15, 9), (17, 9), (16, 9), (10, 9), (11, 9),
                     (9, 8), (1, 14), (14, 1), (0, 14), (14, 0)}


class Tokenizer:
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
                self.tokens.append(stl.IdToken(line_num, part))
            elif is_float(part):
                self.tokens.append(stl.NumToken(line_num, part))
            elif is_integer(part):
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
        """
        Looks for import statement between the given slice of the tokens list.

        :param from_: the beginning position of search
        :param to: the end position of search
        :return: None
        """
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
        """
        Imports an external sp file.

        This method tokenizes the imported file, and inserts all tokens except the EOF token of the imported
        file into the current file.

        :param full_path: the path of the file to be imported
        :return: None
        """
        with open(full_path, "r") as file:
            lexer = Tokenizer()
            lexer.file_name = full_path
            lexer.script_dir = get_dir(full_path)
            lexer.tokenize(file)
            # print(lexer.tokens)
            self.tokens += lexer.tokens
            self.tokens.pop()  # remove the EOF token

    def get_tokens(self):
        """
        Returns the tokens list.

        :return: the tokens list
        """
        return self.tokens


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

            for i in range(1, len(string), 1):
                char = string[i]
                t = char_type(char)
                if (t in SELF_CONCATENATE and t == last_type) or ((last_type, t) in CROSS_CONCATENATE):
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
    elif ch.isalpha():
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
    elif ch == "_":
        return 14
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
    else:
        return -1


def is_integer(num_str: str) -> bool:
    """

    :param num_str:
    :return:
    """
    if len(num_str) == 0:
        return False
    for ch in num_str:
        if not ch.isdigit() and ch != "_":
            return False
    return True


def is_float(num_str: str) -> bool:
    """
    :param num_str:
    :return:
    """
    if "." in num_str:
        index = num_str.index(".")
        front = num_str[:index]
        back = num_str[index + 1:]
        if len(front) > 0:
            if not is_integer(front):
                return False
        if is_integer(back):
            return True
    return False


def get_dir(f_name: str):
    if os.sep in f_name:
        return f_name[:f_name.find(os.sep)]
    elif "/" in f_name:
        return f_name[:f_name.find("/")]
    else:
        return ""
