import "math";


println(getcwf());
let t1 = system.time();
let d = factorization(123);
println(d);
//a = primes(100000);
//print(a.length());
//println(fib(15));
let t2 = system.time();
println("time used: " + string(t2 - t1) + " ms");
