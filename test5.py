def fib(n):
    if n < 2:
        return n
    else:
        x = n - 1
        y = n - 2
        a = fib(x)
        b = fib(y)
        c = a + b
        return c


if __name__ == "__main__":
    print(fib(7))
