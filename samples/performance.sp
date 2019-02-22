function fib(n) {
    if (n < 2) {
        n;
    } else {
        fib(n - 1) + fib(n - 2);
    };
};

t0 = system.time();

p = 0;
while (p < 100000) {
    p += 1;
};

t1 = system.time();
print(t1 - t0);

fib(20);

t2 = system.time();
print(t2 - t1);

import "algorithm";

lst = list();

lst = rand_list(100, -32768, 32767);

t3 = system.time();
merge_sort(lst);
t4 = system.time();

print(t4 - t3);
