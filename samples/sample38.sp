function g(a, b, c=1, d=0, e=1) {
    return a * b * c - d * e;
}

function decor(func) {
    function pt(*args, **kwargs) {
        assert kwargs.size() >= 0;
        println("fucked!");
        func(*args, **kwargs);
    }
    return pt;
}

var f = decor(g);
println(f(3, 4, 2, d=1, e=2));
println(not (true is true));
