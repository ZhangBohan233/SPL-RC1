function rec(x, y) {
    if (y > 0) {
        a = x + 1;
        b = y - 1;
        rec(a, b);
    } else {
        x;
    };
};

s = rec(0, 5);
