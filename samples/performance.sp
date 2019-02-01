function fib(n) {
    if (n < 2) {
        n;
    } else {
        fib(n - 1) + fib(n - 2);
    };
};

t0 = time();

i = 0;
while (i < 1000000) {
    i = i + 1;
};

t1 = time();
print(t1 - t0);

fib(25);

t2 = time();
print(t2 - t1);
