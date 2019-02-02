function f(a) {
    function (b) {
        function () {
            a = a + b;
        };
    };
};

n0=f(2);
n1=n0(3);
x = n1();
x = n1();
