import os


OPTION_FILE = "options.ini"


def check_file():
    if not os.path.exists(OPTION_FILE):
        with open(OPTION_FILE, "w") as f:
            f.write("gc_size=128mb\n")


def load():
    check_file()

    d = {}
    with open(OPTION_FILE, "r") as f:
        for line in f.readlines():
            if "=" in line:
                lst = [x.strip() for x in line.split("=")]
                d[lst[0]] = lst[1]

    return d


def get_gc_size():
    opt = load()
    gc_size: str = opt.get("gc_size", "128mb")
    multiplier = 1
    if gc_size[-2:].isalpha():
        word = gc_size[-2:]
        real = gc_size[:-2]
        if word == "kb":
            multiplier = 1024
        elif word == "mb":
            multiplier = 1048576
        elif word == "gb":
            multiplier = 1_073_741_824
    else:
        real = gc_size
    return int(real) * multiplier // 32
