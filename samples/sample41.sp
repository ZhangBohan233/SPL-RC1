if (main()) {
    const st = system.time();

    var arr = new int[10000];
    for (var i = 0; i < 10000; i += 1) {
        arr[i] = i;
    }
    const end = system.time();
    println(end - st);
}