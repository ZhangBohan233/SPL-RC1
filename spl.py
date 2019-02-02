""" The main SPL runner. """

import sys
import spl_lexer2
import spl_parser2
import spl_interpreter
import time

HELP = """
spl.py 
"""


def parse_arg(args):
    d = {"file": None, "debugger": False, "timer": False, "ast": False, "tokens": False, "vars": False, "argv": [],
         "exit": False}
    for i in range(1, len(args), 1):
        arg = args[i]
        if d["file"] is not None:
            d["argv"].append(arg)
        else:
            if arg[0] == "-":
                flag = arg[1:]
                if flag == "debug":
                    d["debugger"] = True
                elif flag == "timer":
                    d["timer"] = True
                elif flag == "ast":
                    d["ast"] = True
                elif flag == "tokens":
                    d["tokens"] = True
                elif flag == "vars":
                    d["vars"] = True
                elif flag == "exit":
                    d["exit"] = True
                else:
                    print("unknown flag: -" + flag)
            elif arg == "help":
                pass
            else:
                d["file"] = arg
                d["argv"].append(arg)
    if d["file"] is None:
        print_usage()
        return None
    else:
        return d


def print_usage():
    print(HELP)


if __name__ == "__main__":
    argv = parse_arg(sys.argv)
    if not argv:
        exit(0)

    file_name = argv["file"]

    f = open(file_name, "r")

    try:
        lex_start = time.time()

        lexer = spl_lexer2.Lexer(f)
        lexer.tokenize()

        if argv["tokens"]:
            print(lexer.tokens)

        parse_start = time.time()

        psr = lexer.parse()
        if argv["ast"]:
            print(psr)
        if argv["debugger"]:
            spl_interpreter.DEBUG = True

        block = spl_parser2.BlockStmt()
        block.lines = psr.elements

        interpret_start = time.time()

        itr = spl_interpreter.Interpreter(block, argv["argv"])
        result = itr.interpret()

        end = time.time()

        if argv["exit"]:
            print("Process finished with exit value " + str(result))

        if argv["vars"]:
            print(itr.env.variables)
            print("Heap: " + str(itr.env.heap))

        if argv["timer"]:
            print("Time used: tokenize: {}s, parse: {}s, execute: {}s.".format
                  (parse_start - lex_start, interpret_start - parse_start, end - interpret_start))

    except Exception as e:
        raise e
    finally:
        f.close()
