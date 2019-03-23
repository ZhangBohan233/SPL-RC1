import sys


def count_char(text: str, char: str) -> int:
    count = text.count(char.lower())
    count += text.count(char.upper())
    return count


def count_file(file_name: str, char: str) -> int:
    with open(file_name, "r") as f:
        t = f.read()
        return count_char(t, char)


def count_alphabet(file_name: str) -> dict:
    d = {}
    for ch in "abcdefghijklmnopqrstuvwxyz":
        d[ch] = count_file(file_name, ch)
    return d


if __name__ == "__main__":
    args_ = sys.argv
    fn = args_[1]
    c = count_alphabet(fn)
    print(c)
    lst = [(ch, c[ch]) for ch in c]
    lst.sort(key=lambda k: k[1], reverse=True)
    print(lst)
