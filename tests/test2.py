if __name__ == "__main__":
    import spl_ast

    psr = spl_ast.Parser()
    psr.add_name("a")
    psr.add_assignment()
    psr.add_number("3")
    psr.add_operator("+")
    psr.add_number("2")
    psr.add_operator("*")
    psr.add_number("5")
    psr.add_operator("+")
    psr.add_number("4")
    psr.build_expr()
    psr.build_line()

    print(psr)

    import spl_interpreter

    itr = spl_interpreter.Interpreter(psr.get_as_block())
    print(itr.interpret())
    print(itr.env.variables)
