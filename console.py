import spl_interpreter
import spl_lexer as lex
import spl_token_lib as stl
import spl_parser as psr


if __name__ == "__main__":

    line_terminated = True

    lex2 = lex.Tokenizer()
    itr = spl_interpreter.Interpreter([], "utf8")
    lines = []

    while True:

        if line_terminated:
            line = input(">>> ")
        else:
            line = input("... ")
        lines.append(line)

        try:
            lex2.tokenize(lines)

            parser_ = psr.Parser(lex2.get_tokens())
            block = parser_.parse()

            itr.set_ast(block)
            res = itr.interpret()
            # print(res)

            lines.clear()
            line_terminated = True
        except stl.ParseException:
            line_terminated = False
        except Exception as e:
            print(e)
            lines.clear()
            line_terminated = True
