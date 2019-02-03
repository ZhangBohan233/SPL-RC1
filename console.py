def check_ended(ls):
    return True


if __name__ == "__main__":
    import spl_interpreter
    import spl_lexer

    line_terminated = True

    lexer = spl_lexer.Lexer()
    itr = spl_interpreter.Interpreter([])
    lines = []
    while True:
        if line_terminated:
            line = input(">>>")
        else:
            line = input("...")
        lines.append(line)

        line_terminated = check_ended(lines)

        if line_terminated:
            lexer.tokenize(lines)
            block = lexer.parse()

            itr.set_ast(block)
            res = itr.interpret()
            print(res)

            lines.clear()
