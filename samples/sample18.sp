import "math";

t1 = system.time();
d = factorization(341);
print(d);
t2 = system.time();
print("time used: " + string(t2 - t1) + " ms");
