function f(a) {
    function (b) {
        function () {
            a = a + b;
        };
    };
};

d = f(3)=>(2)=>();
print(d);
