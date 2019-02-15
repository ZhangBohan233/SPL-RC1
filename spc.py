import spl_coder as cdr
import spl_lexer as lxr
import spl_parser as psr
import sys


if __name__ == "__main__":
    file_name = sys.argv[1]

    f = open(file_name, "r")

    lexer = lxr.Lexer()
    lexer.script_dir = sys.argv[1]
    lexer.file_name = file_name
    lexer.tokenize(f)

    block = lexer.parse()

    c = cdr.Coder()
    byt = c.make_code(block)
    # print(list(byt))

    wf = open(file_name + "e", "wb")
    wf.write(byt)
    wf.close()

    f.close()
