def fib(n):
    if n < 2:
        return n
    else:
        a = fib(n - 1)
        b = fib(n - 2)
        return a + b


def curry(a):
    def inner():
        return a + 1
    return inner


if __name__ == "__main__":
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
