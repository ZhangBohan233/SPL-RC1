import "math";

t1 = time();
d = factorization(255);
print(d);
t2 = time();
print("time used: " + string(t2 - t1) + " ms");
