function fib(n) {
    if (n < 2) {
        n;
    } else {
        x = n - 1;
        y = n - 2;
        a = fib(x);
        b = fib(y);
        a + b;
    };
};

a = time();
x = fib(20);
b = time();
c = b - a;
print(c);
print(x);
