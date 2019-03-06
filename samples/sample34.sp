import "string_builder"


def ternary(n) {
    var s = "";
    while (n > 0) {
        s = string(n % 3) + s;
        n = n / 3;
    }
    return s;
}


if (main()) {
    println(var a = ternary(344));
    var b = new StringBuilder();
    b.append(3);
    b.append("r");
    println(b.length());
    var c = string(b);
    b.append(66);
    println(b);

    var d = list(1, 2, 3, 4);
    d[1] += 1;
    println(d);
}
