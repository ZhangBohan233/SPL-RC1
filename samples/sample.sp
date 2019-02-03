function exp(base, exp) {
    count = 0;
    res = 1;
    while (count < exp) {
        res = res * base;
        count = count + 1;
    };
    res;
};

a = 2;
exp(a, 3);
