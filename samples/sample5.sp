class Fuck {
    x = 2;
};

class Sample {
    a = 1;
    b = new Fuck;

    function m() {
        a + b.x;
    };

    function set_a(na) {
        a = na;
    };
};

ca = new Sample;
ca.set_a(3);
d = ca.a;
d;
