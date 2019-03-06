""" The main SPL runner. """

import sys
import spl_lexer
import spl_interpreter
import spl_parser as psr
import time
import os
import spl_optimizer as opt
import spl_token_lib as stl
import spl_lib as lib

sys.setrecursionlimit(10000)

EXE_NAME = "spl.py"

INSTRUCTION = """Welcome to Slowest Programming Language.

Try "{} help" to see usage.""".format(EXE_NAME)

HELP = """Name
    {}  -  Slowest Programming Language command line interface.

Usage
    {} [OPTIONS]... [FLAGS]... FILE [ARGV]...
    
Description
OPTIONS:    
    -a,   -ast,     --abstract syntax tree    shows the structure of the abstract syntax tree     
    -d,   -debug,   --debugger                enables debugger
    -et,            --execution               shows the execution times of each node
    -e,   -exit,    --exit value              shows the program's exit value
    -o1,            --optimize 1              enable level 1 optimization
    -o2,            --optimize 2              enable level 2 optimization
    -t,   -timer,   --timer                   enables the timer
    -tk,  -tokens,  --tokens                  shows language tokens
    -v,   -vars,    --variables               prints out all global variables after execution
    
FLAGS:
    -Dfile ENCODING    --file encoding    changes the sp file decoding
    
ARGV:
    command-line argument for the spl program
    
Example
    {} -ast -tokens example.sp -something
""".format(EXE_NAME, EXE_NAME, EXE_NAME)


def parse_arg(args):
    d = {"file": None, "dir": None, "debugger": False, "timer": False, "ast": False, "tokens": False,
         "vars": False, "argv": [], "encoding": None, "exit": False, "optimize": 0, "exec_time": False,
         "spe": False, "doc": None}
    # for i in range(1, len(args), 1):
    i = 1
    while i < len(args):
        arg: str = args[i]
        if d["file"] is not None:
            d["argv"].append(arg)
        else:
            if arg[0] == "-":
                flag = arg[1:]
                if flag == "d" or flag == "debug":
                    d["debugger"] = True
                elif flag == "t" or flag == "timer":
                    d["timer"] = True
                elif flag == "a" or flag == "ast":
                    d["ast"] = True
                elif flag == "tk" or flag == "tokens":
                    d["tokens"] = True
                elif flag == "v" or flag == "vars":
                    d["vars"] = True
                elif flag == "e" or flag == "exit":
                    d["exit"] = True
                elif flag == "Dfile":
                    i += 1
                    d["encoding"] = args[i]
                elif flag == "et":
                    d["exec_time"] = True
                elif flag == "o1":
                    d["optimize"] = 1
                elif flag == "o2":
                    d["optimize"] = 2
                else:
                    print("unknown flag: -" + flag)
            elif arg.lower() == "help":
                print_help()
                return None
            else:
                d["file"] = arg
                d["dir"] = spl_lexer.get_dir(arg)
                d["doc"] = stl.get_doc_name(arg)
                d["argv"].append(arg)
        i += 1
    if d["file"] is None:
        print_usage()
        return None
    else:
        return d


def print_usage():
    print(INSTRUCTION)


def print_help():
    print(HELP)


def interpret():
    lex_start = time.time()

    lexer = spl_lexer.Tokenizer()
    lexer.setup(file_name, argv["dir"], argv["doc"])
    lexer.tokenize(f)

    if argv["tokens"]:
        print(lexer.tokens)

    parse_start = time.time()

    parser = psr.Parser(lexer.get_tokens())
    block = parser.parse()

    o_level = argv["optimize"]

    if o_level > 0:
        optimizer = opt.Optimizer(block)
        optimizer.optimize(o_level)
        block = optimizer.ast

    if argv["ast"]:
        print("===== Abstract Syntax Tree =====")
        print(block)
        print("===== End of AST =====")
    if argv["debugger"]:
        spl_interpreter.DEBUG = True

    interpret_start = time.time()

    itr = spl_interpreter.Interpreter(argv["argv"], encoding)
    itr.set_ast(block)
    result = itr.interpret()

    end = time.time()

    sys.stdout.flush()
    sys.stderr.flush()

    if argv["exit"]:
        print("Process finished with exit value " + lib.replace_bool_none(str(result)))

    if argv["vars"]:
        print(itr.env)

    if argv["timer"]:
        print("Time used: tokenize: {}s, parse: {}s, execute: {}s.".format
              (parse_start - lex_start, interpret_start - parse_start, end - interpret_start))

    if argv["exec_time"]:
        print(block)


class ArgumentsException(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)


if __name__ == "__main__":
    argv = parse_arg(sys.argv)
    if argv:
        file_name = argv["file"]

        if not os.path.exists(file_name):
            print("File Not Found!")
            exit(1)

        if file_name[-3:] == ".sp":
            encoding = argv["encoding"]
            if encoding is not None:
                assert isinstance(encoding, str)
                f = open(file_name, "r", encoding=encoding)
            else:
                f = open(file_name, "r")

            try:
                interpret()
            except Exception as e:
                raise e
            finally:
                f.close()
                try:
                    os.remove(argv["doc"])
                finally:
                    pass
        else:
            raise ArgumentsException("SPL scripts must ended with '.sp'.")
