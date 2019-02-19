import sys
import os
import spl_coder as cdr
import spl_decompiler as dec

EXE_NAME = "spd.py"

HELP = """Name
    {}  -  Slowest Programming Language Decompiler.

Usage
    {} [OPTIONS]... [FLAGS]... FILE

Description

FLAGS:
    -f OUT_FILE,    --out file name       output to file

Example
    {} -f example.txt example.spe
    
WARNING:
    This decompiler does not guarantee the correctness of the decompile result. Please do not use this to generate
    the source code.
""".format(EXE_NAME, EXE_NAME, EXE_NAME)


def parse_args():
    argv_ = sys.argv
    d = {"file": None, "out_file": None}

    if len(argv_) == 1:
        print(HELP)
        return None

    i = 1
    while i < len(argv_):
        arg: str = argv_[i]
        if arg[0] == "-":
            flag = arg[1:]
            if flag == "f":
                i += 1
                d["out_file"] = argv_[i]
        elif arg.lower() == "help":
            print(HELP)
            return None
        else:
            if len(arg) > 3 and arg[-3:] == ".sp":
                print("Cannot decompile source codes.")
                return None
            else:
                if not os.path.exists(arg):
                    print("File does not exist.")
                    return None
                d["file"] = arg
        i += 1

    return d


if __name__ == "__main__":
    argv = parse_args()
    if argv is not None:
        f = open(argv["file"], "rb")

        try:
            decoder = cdr.Decoder(f)
            ast = decoder.decode()
            decompiler = dec.Decompiler(ast)
            text = decompiler.decompile()

            of_name = argv["out_file"]
            if of_name:
                wf = open(of_name, "w")
                wf.write(text)
                wf.close()
            else:
                print(text)
                input("Press ENTER to exit")
        finally:
            f.close()
