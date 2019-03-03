class Object {
    var attr1;
    function Object(a) {
        attr1 = a;
    }

    function increment() {
        attr1 += 1;
    }

    function __getitem__(index) {

    }

    operator +(other) {
        return new Object(attr1 + other.attr1);
    }
}

if (main()) {
    var a;
    println(dir(Object));
    for (var i = 0; i < 10; i += 1) {
        a = new Object(i);
        println(a);
    }

}
