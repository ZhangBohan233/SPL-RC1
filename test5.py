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


if __name__ == "__main__":
    x = f(2)()
    print(x)

    # import time
    # s = time.time() * 1000
    # # print(fib(25))
    # x = 0
    # while x < 1000000:
    #     x = x + 1
    # e = time.time() * 1000
    # print(e - s)
    # # x = curry(2)
    # # print(x())
