def fib(n):
    if n < 2:
        return n
    else:
        a = fib(n - 1)
        b = fib(n - 2)
        return a + b


def f(a):
    def g():
        return a + 1
    return g


class N:
    def __init__(self):
        self.type = 0


class N2(N):
    def __init__(self):
        N.__init__(self)

        self.type = 1


class N3(N):
    def __init__(self):
        N.__init__(self)

        self.type = 2


if __name__ == "__main__":
    # x = f(2)()
    # print(x)

    import time
    s = time.time() * 1000
    # print(fib(25))
    x = 0
    while x < 1000000:
        x = x + 1
    e = time.time() * 1000
    print(e - s)
    # x = curry(2)
    # print(x())

    # import time
    # lst = []
    # for i in range(1000000):
    #     lst.append(N2())
    #     lst.append(N3())
    #
    # n2c = 0
    # n3c = 0
    # t1 = time.time()
    # for x in lst:
    #     if x.type == 1:
    #         n2c += 1
    #     elif x.type == 2:
    #         n3c += 1
    #     # if isinstance(x, N2):
    #     #     n2c += 1
    #     # elif isinstance(x, N3):
    #     #     n3c += 1
    # t2 = time.time()
    # print("time: " + str(t2 - t1))
    # print(n2c)
    # print(n3c)
