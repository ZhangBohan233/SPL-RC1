function fib(n) {
    if (n < 2) {
        n;
    } else {
        fib(n - 1) + fib(n - 2);
    };
};

t0 = system.time();

i = 0;
while (i < 1000000) {
    i = i + 1;
};

t1 = system.time();
print(t1 - t0);

fib(25);

t2 = system.time();
print(t2 - t1);

import "algorithm";

lst = list();

lst = rand_list(1000, -32768, 32767);

t3 = system.time();
merge_sort(lst);
t4 = system.time();

print(t4 - t3);
