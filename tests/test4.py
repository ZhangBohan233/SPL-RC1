if __name__ == "__main__":
    import spl_ast
    psr = spl_ast.Parser()

    # n = 5;
    psr.add_name("n")
    psr.add_assignment()
    psr.add_number("5")
    psr.build_line()

    # if (n < 10)
    psr.add_if()
    psr.add_name("n")
    psr.add_operator("<")
    psr.add_number("10")
    psr.build_expr()
    psr.build_condition()

    # {
    # a = 1;
    # }
    psr.new_block()
    psr.add_name("a")
    psr.add_assignment()
    psr.add_number("1")
    psr.build_line()

    # if (a == 1)
    psr.add_if()
    psr.add_name("a")
    psr.add_operator("==")
    psr.add_number("1")
    psr.build_expr()
    psr.build_condition()

    # {
    # b = 2;
    # }
    psr.new_block()
    psr.add_name("b")
    psr.add_assignment()
    psr.add_number("2")
    psr.build_line()
    psr.build_block()
    psr.build_line()

    psr.build_block()
    psr.build_line()

    psr.add_name("b")
    psr.build_line()

    print(psr)

    block = spl_ast.BlockStmt()
    block.lines = psr.elements

    import spl_interpreter

    itr = spl_interpreter.Interpreter(block)
    print(itr.interpret())
    print(itr.env.variables)
