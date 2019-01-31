function f(a) {
    function (b) {
        function () {
            a = a + b;
        };
    };
};

ff = f(2);
gg = ff(3);
gg();
gg();
gg();
gg();
