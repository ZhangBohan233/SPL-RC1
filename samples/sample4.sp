function fib(n) {
    if (n < 2) {
        n;
    } else {
        a = fib(n-1);
        b = fib(n-2);
        a + b;
    };
};

a = time();
x = fib(25);
b = time();
print(b - a);
print(x);
