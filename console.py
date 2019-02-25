import spl_interpreter
import spl_token_lib as stl


if __name__ == "__main__":

    # import spl_lexer

    line_terminated = True

    lex2 = spl_interpreter.lex.Lexer()
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
            block = lex2.parse()

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
