class Object {
    var attr1;
    function Object(a=0, b=5) {
        attr1 = a + b;
    }

    function increment() {
        attr1 += 1;
    }

    function __getitem__(index) {

    }

    function copy(plus) {
        return new Object(attr1 + plus, b=0);
    }

    operator +(other) {
        return new Object(attr1 + other.attr1, 0);
    }
}

function duck(a, b=1, c=2, d=3) {
    return a + b + c + d;
}

if (main()) {
    var a = new Object(1, 2);
    println(a);
    a.attr1 += 1;
    println(a);
}
