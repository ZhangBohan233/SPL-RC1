class Integer {
    var value;
    def Integer(v) {
        value = v;
    }

    def __repr__() {
        return string(value);
    }
}


if (main()) {
    const st = system.time();

    var arr = new Integer[1000];
    for (var i = 0; i < 1000; i += 1) {
        arr[i] = new Integer(i);
    }
    const end = system.time();
    println(end - st);
}