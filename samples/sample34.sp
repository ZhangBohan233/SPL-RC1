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
    b.append(66);
    var c = string(b);
    println(b);
    println(b.substring(1, 4));
}
