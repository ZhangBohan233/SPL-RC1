import "threading"

def test(a, b=0) {
    for (var i = 0; i < a + b; i += 1) {
        println(i);
    }
    system.sleep(1000);
}

def loop() {
    var i = 0;
    while (i < 10_000) {
        i += 1;
    }
    println(i);
}

if (main()) {

    var threads = list();

    for (var i = 0; i < 8; i += 1) {
        threads.append(new Thread("loop", list()));
    }

    var start = system.time();

    for (var i = 0; i < 8; i += 1) {
        loop();
    }
    //for (var th; threads) {
    //    th.start();
    //}

    await_all(threads);

    var stop = system.time();
    println(stop - start);
}
