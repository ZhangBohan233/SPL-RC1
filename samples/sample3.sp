function f(a) {
    if (a < 1) {
        a;
    } else {
        f(a-1);
    };
};

f(5);
