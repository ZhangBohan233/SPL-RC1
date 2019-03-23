def test(a, b=0, c=1, d=2):
    return a + b + c + d


def err():
    print()
    raise Exception()


if __name__ == "__main__":
    import time

    d = {}
    n = 1000000
    for i in range(n):
        d[i] = i

    st = time.time()
    e = lambda k: err()
    for i in range(n + 1):
        d.setdefault(i, e)
        # if i not in d:
        #     pass
        # else:
        #     d[i] = 9
    ed = time.time()
    print("time: {} s".format(ed - st))
    # print(d)
