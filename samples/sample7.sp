function f(a) {
    var a;
    function (b) {
        var b;
        function () {
            a = a + b;
        }
    }
}

let d = f(3)=>(2)=>();
println(d);

let a = 1;
if (a < 2) {
    a += 1;
}
println(a);
