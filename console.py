import spl_interpreter


def check_ended(ls):
    return True


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

        line_terminated = check_ended(lines)

        if line_terminated:
            lex2.tokenize(lines)
            block = lex2.parse()

            itr.set_ast(block)
            res = itr.interpret()
            print(res)

            lines.clear()
