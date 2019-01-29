function exp(base, exp) {
    count = 0;
    res = 1;
    while (count < exp) {
        res = res * base;
        count = count + 1;
    };
    res;
};

f = exp;
//res = f(1, 2);
res = f(2, 3);
