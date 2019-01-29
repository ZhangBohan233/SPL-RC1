function test(a, b) {
    c = 1;
    if (a > 3) {
        c = 0;
        if (a > 4) {
            c = 2;
        };
    };
    c;
};

res = test(5, 6);
