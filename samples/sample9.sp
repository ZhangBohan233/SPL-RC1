function test(a) {
    c = 0;
    if (a > 2) {
        c = 1;
        return c;
    } else {
        c = 5;
        return c;
    }
    c = 2;
    return c;
};

c = test(0);
