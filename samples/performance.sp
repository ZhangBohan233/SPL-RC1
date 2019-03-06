import "algorithm";

if (main()) {
    const t0 = system.time();

    for (var i = 0; i < 1000000; i += 1);

    const t1 = system.time();
    println(t1 - t0);

    fib(25);

    const t2 = system.time();
    println(t2 - t1);

    const lst = rand_list(1000, -32768, 32767);

    const t3 = system.time();
    merge_sort(lst);
    const t4 = system.time();

    println(t4 - t3);
}
