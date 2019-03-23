function f(a, b) {
    if (a < 1) {
        a;
    } else {
        f(a-1, b);
    };
};

print(f(5, 4));
