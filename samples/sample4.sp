function fib(n) {
    if (n < 2) {
        n;
    } else {
        fib(n - 1) + fib(n - 2);
    };
};

a = time();
x = fib(20);
b = time();
c = b - a;
print(c);
print(x);
