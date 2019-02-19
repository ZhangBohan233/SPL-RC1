import spl_coder as cdr
import spl_interpreter as itr
import spl_decompiler as dec


if __name__ == "__main__":
    inf = open("../samples/sample23.spe", "rb")
    decoder = cdr.Decoder(inf)
    ast = decoder.decode()
    # print(ast)

    decompiler = dec.Decompiler(ast)
    s = decompiler.decompile()
    print(s)

    # inter = itr.Interpreter([], "utf-8")
    # inter.set_ast(ast)
    # inter.interpret()
