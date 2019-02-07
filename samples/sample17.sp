
function foo(n) {
    function () {
        n = n + 1;
        return n;
    }
}
f = foo(3)=>();

print(f);
