""" The main SPL runner. """

import sys
import spl_lexer
import spl_parser
import spl_interpreter
import time

if __name__ == "__main__":
    argv = sys.argv

    file_name = argv[1]

    f = open(file_name, "r")

    lex_start = time.time()

    lexer = spl_lexer.Lexer(f)
    lexer.read()

    # print(lexer.tokens)

    parse_start = time.time()

    psr = lexer.parse()
    # print(psr)

    block = spl_parser.BlockStmt()
    block.lines = psr.elements

    interpret_start = time.time()

    itr = spl_interpreter.Interpreter(block)
    result = itr.interpret()

    end = time.time()

    print("Process finished with exit code " + str(result))

    print("Time used: tokenize: {}s, parse: {}s, execute: {}s.".format
          (parse_start - lex_start, interpret_start - parse_start, end - interpret_start))
    # print(itr.interpret())
    # print(itr.env.variables)
    # print(itr.env.heap)
