if __name__ == "__main__":
    import spl_ast
    psr = spl_ast.Parser()

    psr.add_function("main")
    psr.build_func_params(["x", "y"])

    psr.new_block()

    psr.add_name("a")
    psr.add_assignment()
    # psr.add_number("5")
    psr.add_name("x")
    psr.add_operator("+")
    psr.add_number("2")
    # psr.build_expr()
    psr.add_operator("*")
    psr.add_number("3")
    psr.build_expr()
    psr.build_line()

    psr.add_if()
    psr.add_name("a")
    psr.add_operator(">")
    psr.add_number("2")
    psr.build_expr()
    psr.build_condition()

    psr.new_block()
    psr.add_name("b")
    psr.add_assignment()
    psr.add_name("a")
    psr.add_operator("+")
    psr.add_number("1")
    psr.build_expr()
    # print(psr.inner.stack)
    psr.build_line()
    # print(psr.inner)
    psr.build_block()

    psr.add_else()

    psr.new_block()
    psr.add_name("b")
    psr.add_assignment()
    psr.add_number("8")
    psr.build_expr()
    psr.build_line()
    psr.build_block()

    psr.build_line()

    psr.add_while()
    psr.add_name("b")
    psr.add_operator(">")
    psr.add_number("0")
    psr.build_expr()
    psr.build_condition()

    psr.new_block()
    psr.add_name("b")
    psr.add_assignment()
    psr.add_name("b")
    psr.add_operator("-")
    psr.add_number("1")
    psr.build_expr()
    psr.build_line()
    psr.build_block()

    psr.build_line()

    psr.add_name("a")
    psr.build_line()

    psr.build_block()
    psr.build_line()

    psr.add_name("res")
    psr.add_assignment()
    psr.add_call("main")
    psr.add_number("3")
    psr.add_number("5")
    psr.build_call()
    # psr.build_expr2()
    psr.build_line()

    print(psr)

    block = spl_ast.BlockStmt()
    block.lines = psr.elements

    import spl_interpreter

    itr = spl_interpreter.Interpreter(block)
    print(itr.interpret())
    print(itr.env.variables)
