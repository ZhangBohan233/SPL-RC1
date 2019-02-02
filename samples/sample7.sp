function f(a) {
    function (b) {
        function () {
            a = a + b;
        };
    };
};

n0=f(2);
n1=n0(3);
n2=n1();
x=n2;
