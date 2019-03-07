import "algorithm";

if (main()) {
    const t0 = system.time();

    for (var i = 0; i < 100_000; i += 1);

    const t1 = system.time();
    println(t1 - t0);

    fib(20);

    const t2 = system.time();
    println(t2 - t1);

    const lst = rand_list(500, -32768, 32767);

    const t3 = system.time();
    merge_sort(lst);
    const t4 = system.time();

    println(t4 - t3);
}
