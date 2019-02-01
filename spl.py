""" The main SPL runner. """

import sys
import spl_lexer
import spl_parser
import spl_interpreter
import time

HELP = """
spl.py 
"""


def parse_arg(args):
    d = {"file": None, "debugger": False, "timer": False, "ast": False, "token": False, "vars": False, "argv": []}
    for i in range(1, len(args), 1):
        arg = args[i]
        if d["file"] is not None:
            d["argv"].append(arg)
        else:
            if arg[0] == "-":
                flag = arg[1:]
                if flag == "debug":
                    d["debugger"] = True
                elif flag == "t":
                    d["timer"] = True
                elif flag == "ast":
                    d["ast"] = True
                elif flag == "token":
                    d["token"] = True
                elif flag == "v":
                    d["vars"] = True
                else:
                    print("unknown flag: -" + flag)
            elif arg == "help":
                pass
            else:
                d["file"] = arg
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

        lexer = spl_lexer.Lexer(f)
        lexer.tokenize()

        if argv["token"]:
            print(lexer.tokens)

        parse_start = time.time()

        psr = lexer.parse()
        if argv["ast"]:
            print(psr)
        if argv["debugger"]:
            spl_interpreter.DEBUG = True

        block = spl_parser.BlockStmt()
        block.lines = psr.elements

        interpret_start = time.time()

        itr = spl_interpreter.Interpreter(block)
        result = itr.interpret()

        end = time.time()

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
