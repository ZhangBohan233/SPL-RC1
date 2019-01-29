if __name__ == "__main__":
    import spl_lexer
    import spl_parser
    import spl_interpreter
    f = open("sample.sp", "r")
    lexer = spl_lexer.Lexer(f)
    lexer.read()

    print(lexer.tokens)

    psr = lexer.parse()
    print(psr)

    block = spl_parser.BlockStmt()
    block.lines = psr.elements

    itr = spl_interpreter.Interpreter(block)
    print(itr.interpret())
    print(itr.env.variables)
