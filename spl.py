""" The main SPL runner. """

import sys
import spl_lexer
# import spl_parser
import spl_interpreter
import time

INSTRUCTION = """Welcome to Slowest Programming Language.

Try "spl.py help" to see usage."""

PY_HELP = """Name
    spl.py  -  Slowest Programming Language command line interface.

Usage
    spl.py [OPTIONS]... FILE [ARGV]...
    
Description
OPTIONS:    
    -ast,    --abstract syntax tree    shows the structure of the abstract syntax tree
    -debug,  --debugger                enables debugger
    -exit,   --exit value              shows the program's exit value
    -timer,  --timer                   enables the timer
    -tokens, --tokens                  shows language tokens
    -vars,   --variables               prints out all global variables after execution
    
ARGV:
    command-line argument for the spl program
    
Example
    spl.py -ast -tokens example.sp -something
"""


def parse_arg(args):
    d = {"file": None, "dir": None, "debugger": False, "timer": False, "ast": False, "tokens": False,
         "vars": False, "argv": [], "exit": False}
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
                print_help()
                return None
            else:
                d["file"] = arg
                d["dir"] = spl_lexer.get_dir(d["file"])
                d["argv"].append(arg)
    if d["file"] is None:
        print_usage()
        return None
    else:
        return d


def print_usage():
    print(INSTRUCTION)


def print_help():
    print(PY_HELP)


if __name__ == "__main__":
    argv = parse_arg(sys.argv)
    if argv:
        file_name = argv["file"]

        f = open(file_name, "r")

        try:
            lex_start = time.time()

            lexer = spl_lexer.Lexer()
            lexer.script_dir = argv["dir"]
            lexer.file_name = file_name
            lexer.tokenize(f)

            if argv["tokens"]:
                print(lexer.tokens)

            parse_start = time.time()

            block = lexer.parse()
            if argv["ast"]:
                print("===== Abstract Syntax Tree =====")
                print(block)
                print("===== End of AST =====")
            if argv["debugger"]:
                spl_interpreter.DEBUG = True

            interpret_start = time.time()

            itr = spl_interpreter.Interpreter(argv["argv"])
            itr.set_ast(block)
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
