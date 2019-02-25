function f(a) {
    var a;
    function (b) {
        var b;
        function () {
            a = a + b;
        }
    }
}

let d = f(3)(2)();
println(d);
