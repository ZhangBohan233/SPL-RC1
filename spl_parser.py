import spl_ast as ast
import spl_token_lib as stl


ABSTRACT_IDENTIFIER = {"function", "def", "class"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        """
        Parses the list of tokens stored in this Lexer, and returns the root node of the parsed abstract syntax
        tree.

        :return: the parsed block
        """
        parser = ast.AbstractSyntaxTree()
        i = 0
        func_count = 0
        in_cond = False
        in_params = False
        is_abstract = False
        var_level = ast.ASSIGN
        call_nest = 0
        brace_count = 0
        class_brace = -1
        extra_precedence = 0
        titles = []

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
                        var_level = ast.CONST
                    elif sym == "var":
                        var_level = ast.VAR
                    # elif sym == "let":
                    #     var_level = ast.LOCAL
                    elif sym == "@":
                        i += 1
                        next_token: stl.IdToken = self.tokens[i]
                        titles.append(next_token.symbol)
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
                            elif in_params:
                                parser.build_func_params()
                                in_params = False
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
                        var_level = ast.ASSIGN
                    elif sym == ":":
                        parser.build_expr()
                        parser.add_type(line)
                    elif sym == ",":
                        # parser.build_expr()
                        if call_nest > 0 or in_params:
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
                        push_back = 1
                        if f_name == "(":
                            f_name = "af-" + str(func_count)
                            func_count += 1
                            push_back = 0
                        parser.add_function(line, f_name, is_abstract, titles.copy())
                        i += push_back
                        in_params = True
                        is_abstract = False
                        titles.clear()
                    elif sym == "operator":
                        i += 1
                        op_token: stl.IdToken = self.tokens[i]
                        op_name = "__" + stl.BINARY_OPERATORS[op_token.symbol] + "__"
                        parser.add_function(line, op_name, False, titles.copy())
                        in_params = True
                        titles.clear()
                        i += 1
                    elif sym == "class":
                        i += 1
                        c_token: stl.IdToken = self.tokens[i]
                        class_name = c_token.symbol
                        parser.add_class((c_token.line_number(), c_token.file_name()), class_name, is_abstract)
                        class_brace = brace_count
                        is_abstract = False
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
                        next_token = self.tokens[i + 1]
                        if isinstance(next_token, stl.IdToken) and next_token.symbol in ABSTRACT_IDENTIFIER:
                            is_abstract = True
                        else:
                            raise stl.ParseException()
                            # parser.add_abstract(line)
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
                        if var_level != ast.ASSIGN:
                            active = parser.get_active()
                            und_vars = active.stack.copy()
                            # print(und_vars)
                            active.stack.clear()
                            for node in und_vars:
                                active.stack.append(node)
                                parser.add_assignment(line, var_level)
                                parser.add_undefined(line)
                                parser.build_line()
                            var_level = ast.ASSIGN
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
