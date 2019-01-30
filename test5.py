def fib(n):
    if n < 2:
        return n
    else:
        a = fib(n - 1)
        b = fib(n - 2)
        return a + b


if __name__ == "__main__":
    import time
    s = time.time() * 1000
    print(fib(25))
    e = time.time() * 1000
    print(e - s)
