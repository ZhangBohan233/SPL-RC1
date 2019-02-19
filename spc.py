import sys
from spl_optimizer import Optimizer
import spl_coder as cdr
import spl_lexer as lex


EXE_NAME = "spc.py"

HELP = """Name
    {}  -  Slowest Programming Language Compiler.
    
Usage
    {} [OPTIONS]... [FLAGS]... FILE
    
Description
OPTIONS:
    -o1,     --optimize level 1
    -o2,     --optimize level 2
    
FLAGS:
    -out OUT_FILE    --out file name      the name of the compiled file
    
Example
    {} -o2 -out example.spe example.sp
""".format(EXE_NAME, EXE_NAME, EXE_NAME)


def parse_args(args):
    d = {"file": None, "out_file": None, "optimize": 0}
    i = 1
    while i < len(args):
        arg: str = args[i]
        # if d["file"] is not None:
        #     pass
        if arg[0] == "-":
            flag = arg[1:]
            if flag == "o1":
                d["optimize"] = 1
            elif flag == "o2":
                d["optimize"] = 2
            elif flag == "out":
                i += 1
                d["out_file"] = args[i]
                if args[i][-3:] == ".sp":
                    print("Out file cannot ends with '.sp'")
                    return None
        elif arg.lower() == "help":
            print(HELP)
            return None
        else:
            d["file"] = arg
            if d["out_file"] is None:
                d["out_file"] = arg + "e"
        i += 1
    return d


if __name__ == "__main__":
    argv = parse_args(sys.argv)

    if argv:
        file_name = argv["file"]
        out_file_name = argv["out_file"]

        lexer = lex.Lexer()
        lexer.setup(file_name, lex.get_dir(file_name))

        f = open(file_name, "r")
        wf = open(out_file_name, "wb")
        lexer.tokenize(f)

        block = lexer.parse()

        if argv["optimize"] > 0:
            op = Optimizer(block)
            op.optimize(argv["optimize"])

        coder = cdr.Coder(block, wf)

        try:
            coder.code()
        finally:
            f.close()
            wf.flush()
            wf.close()
